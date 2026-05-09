import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/task.dart';
import '../providers/task_provider.dart';

class TaskScreen extends StatefulWidget {
  const TaskScreen({super.key});

  @override
  State<TaskScreen> createState() => _TaskScreenState();
}

class _TaskScreenState extends State<TaskScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabCtrl;

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 2, vsync: this);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<TaskProvider>().loadTasks();
    });
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Công việc'),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabCtrl,
          tabs: const [
            Tab(text: 'Chưa xong'),
            Tab(text: 'Đã xong'),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => context.read<TaskProvider>().loadTasks(),
          ),
        ],
      ),
      body: Consumer<TaskProvider>(
        builder: (context, taskProv, _) {
          if (taskProv.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          return TabBarView(
            controller: _tabCtrl,
            children: [
              _TaskList(tasks: taskProv.pendingTasks, showComplete: true),
              _TaskList(tasks: taskProv.completedTasks, showComplete: false),
            ],
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddTaskDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  void _showAddTaskDialog(BuildContext context) {
    final controller = TextEditingController();
    DateTime? selectedDateTime;
    bool isSaving = false;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (dialogContext, setDialogState) {
          Future<void> submit() async {
            if (isSaving) return;
            final text = controller.text.trim();
            if (text.isEmpty) return;

            setDialogState(() => isSaving = true);
            try {
              await context.read<TaskProvider>().addTask(
                text,
                dueTime: selectedDateTime?.toIso8601String(),
              );
              if (ctx.mounted) Navigator.pop(ctx);
            } catch (e) {
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Không lưu được công việc: $e')),
                );
              }
            } finally {
              if (ctx.mounted) {
                setDialogState(() => isSaving = false);
              }
            }
          }

          return AlertDialog(
            title: const Text('Thêm công việc'),
            content: _TaskFormFields(
              controller: controller,
              selectedDateTime: selectedDateTime,
              onPickDateTime: () async {
                final value = await _pickDateTime(ctx, selectedDateTime);
                if (value != null) {
                  setDialogState(() => selectedDateTime = value);
                }
              },
              onClearDateTime: () =>
                  setDialogState(() => selectedDateTime = null),
              onSubmit: submit,
            ),
            actions: [
              TextButton(
                onPressed: isSaving ? null : () => Navigator.pop(ctx),
                child: const Text('Hủy'),
              ),
              FilledButton(
                onPressed: isSaving ? null : submit,
                child: isSaving
                    ? const SizedBox.square(
                        dimension: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Thêm'),
              ),
            ],
          );
        },
      ),
    );
  }

  Future<DateTime?> _pickDateTime(
    BuildContext context,
    DateTime? initial,
  ) async {
    final now = DateTime.now();
    final base = initial ?? now;
    final date = await showDatePicker(
      context: context,
      initialDate: base,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 5),
    );
    if (date == null || !context.mounted) return null;

    final selectedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(base),
    );
    if (selectedTime == null) return null;

    return DateTime(
      date.year,
      date.month,
      date.day,
      selectedTime.hour,
      selectedTime.minute,
    );
  }
}

class _TaskList extends StatelessWidget {
  final List<Task> tasks;
  final bool showComplete;
  const _TaskList({required this.tasks, required this.showComplete});

  @override
  Widget build(BuildContext context) {
    if (tasks.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              showComplete ? Icons.inbox_outlined : Icons.check_circle_outline,
              size: 64,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 16),
            Text(
              showComplete
                  ? 'Không có việc chưa xong'
                  : 'Chưa hoàn thành việc nào',
              style: TextStyle(color: Colors.grey[600], fontSize: 16),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: tasks.length,
      itemBuilder: (context, index) {
        final task = tasks[index];
        return Dismissible(
          key: Key(task.id),
          direction: DismissDirection.endToStart,
          background: Container(
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 20),
            color: Colors.red,
            child: const Icon(Icons.delete, color: Colors.white),
          ),
          confirmDismiss: (_) async {
            return await showDialog<bool>(
              context: context,
              builder: (ctx) => AlertDialog(
                title: const Text('Xóa công việc?'),
                content: Text("Bạn có chắc muốn xóa '${task.title}'?"),
                actions: [
                  TextButton(
                    onPressed: () => Navigator.pop(ctx, false),
                    child: const Text('Hủy'),
                  ),
                  FilledButton(
                    onPressed: () => Navigator.pop(ctx, true),
                    child: const Text('Xóa'),
                  ),
                ],
              ),
            );
          },
          onDismissed: (_) => context.read<TaskProvider>().deleteTask(task.id),
          child: ListTile(
            leading: showComplete
                ? IconButton(
                    icon: const Icon(Icons.radio_button_unchecked),
                    onPressed: () =>
                        context.read<TaskProvider>().completeTask(task.id),
                  )
                : const Icon(Icons.check_circle, color: Colors.green),
            title: Text(
              task.title,
              style: TextStyle(
                decoration: task.isCompleted
                    ? TextDecoration.lineThrough
                    : null,
                color: task.isCompleted ? Colors.grey : null,
              ),
            ),
            subtitle: task.dueTime != null ? Text(task.dueTimeLabel) : null,
            trailing: IconButton(
              icon: const Icon(Icons.edit_outlined),
              tooltip: 'Chỉnh sửa',
              onPressed: () => _showEditTaskDialog(context, task),
            ),
          ),
        );
      },
    );
  }

  void _showEditTaskDialog(BuildContext context, Task task) {
    final controller = TextEditingController(text: task.title);
    DateTime? selectedDateTime = task.dueDateTime?.toLocal();
    bool isSaving = false;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (dialogContext, setDialogState) {
          Future<void> submit() async {
            if (isSaving) return;
            final text = controller.text.trim();
            if (text.isEmpty) return;

            setDialogState(() => isSaving = true);
            try {
              await context.read<TaskProvider>().updateTask(
                task.id,
                title: text,
                dueTime: selectedDateTime?.toIso8601String(),
                clearDueTime: selectedDateTime == null,
              );
              if (ctx.mounted) Navigator.pop(ctx);
            } catch (e) {
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Không lưu được công việc: $e')),
                );
              }
            } finally {
              if (ctx.mounted) {
                setDialogState(() => isSaving = false);
              }
            }
          }

          return AlertDialog(
            title: const Text('Chỉnh sửa công việc'),
            content: _TaskFormFields(
              controller: controller,
              selectedDateTime: selectedDateTime,
              onPickDateTime: () async {
                final value = await _pickDateTime(ctx, selectedDateTime);
                if (value != null) {
                  setDialogState(() => selectedDateTime = value);
                }
              },
              onClearDateTime: () =>
                  setDialogState(() => selectedDateTime = null),
              onSubmit: submit,
            ),
            actions: [
              TextButton(
                onPressed: isSaving ? null : () => Navigator.pop(ctx),
                child: const Text('Hủy'),
              ),
              FilledButton(
                onPressed: isSaving ? null : submit,
                child: isSaving
                    ? const SizedBox.square(
                        dimension: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Lưu'),
              ),
            ],
          );
        },
      ),
    );
  }

  Future<DateTime?> _pickDateTime(
    BuildContext context,
    DateTime? initial,
  ) async {
    final now = DateTime.now();
    final base = initial ?? now;
    final date = await showDatePicker(
      context: context,
      initialDate: base,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 5),
    );
    if (date == null || !context.mounted) return null;

    final selectedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(base),
    );
    if (selectedTime == null) return null;

    return DateTime(
      date.year,
      date.month,
      date.day,
      selectedTime.hour,
      selectedTime.minute,
    );
  }
}

class _TaskFormFields extends StatelessWidget {
  final TextEditingController controller;
  final DateTime? selectedDateTime;
  final VoidCallback onPickDateTime;
  final VoidCallback onClearDateTime;
  final Future<void> Function() onSubmit;

  const _TaskFormFields({
    required this.controller,
    required this.selectedDateTime,
    required this.onPickDateTime,
    required this.onClearDateTime,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    final dueLabel = selectedDateTime == null
        ? 'Chưa chọn ngày giờ'
        : '${selectedDateTime!.day.toString().padLeft(2, '0')}/'
              '${selectedDateTime!.month.toString().padLeft(2, '0')}/'
              '${selectedDateTime!.year} '
              '${selectedDateTime!.hour.toString().padLeft(2, '0')}:'
              '${selectedDateTime!.minute.toString().padLeft(2, '0')}';

    return SizedBox(
      width: 360,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: controller,
            autofocus: true,
            decoration: const InputDecoration(
              hintText: 'Tên công việc...',
              border: OutlineInputBorder(),
            ),
            textInputAction: TextInputAction.done,
            onSubmitted: (_) {
              onSubmit();
            },
          ),
          const SizedBox(height: 12),
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.event_outlined),
            title: const Text('Ngày giờ'),
            subtitle: Text(dueLabel),
            trailing: selectedDateTime == null
                ? null
                : IconButton(
                    icon: const Icon(Icons.close),
                    tooltip: 'Xóa ngày giờ',
                    onPressed: onClearDateTime,
                  ),
            onTap: onPickDateTime,
          ),
        ],
      ),
    );
  }
}
