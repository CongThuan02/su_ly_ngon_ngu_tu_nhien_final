import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cài đặt'),
        centerTitle: true,
      ),
      body: ListView(
        children: [
          const SizedBox(height: 8),
          FutureBuilder<SharedPreferences>(
            future: SharedPreferences.getInstance(),
            builder: (context, snapshot) {
              final name = snapshot.data?.getString('user_name') ?? 'User';
              return ListTile(
                leading: CircleAvatar(child: Text(name[0].toUpperCase())),
                title: Text(name),
                subtitle: const Text('Tài khoản'),
              );
            },
          ),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('Về ứng dụng'),
            subtitle: const Text('Task Bot v1.0 - Chatbot quản lý công việc'),
            onTap: () {
              showAboutDialog(
                context: context,
                applicationName: 'Task Bot',
                applicationVersion: '1.0.0',
                children: [
                  const Text('Chatbot quản lý công việc hàng ngày sử dụng NLP tiếng Việt.\n\n'
                      'Kiến trúc: LSTM + PhoBERT (3 tầng)\n'
                      'Backend: Python FastAPI\n'
                      'Frontend: Flutter'),
                ],
              );
            },
          ),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Đăng xuất', style: TextStyle(color: Colors.red)),
            onTap: () async {
              final prefs = await SharedPreferences.getInstance();
              await prefs.clear();
              if (context.mounted) {
                Navigator.pushNamedAndRemoveUntil(context, '/login', (_) => false);
              }
            },
          ),
        ],
      ),
    );
  }
}
