import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:task_bot/main.dart';

void main() {
  testWidgets('shows login screen when user is not saved', (
    WidgetTester tester,
  ) async {
    SharedPreferences.setMockInitialValues({});

    await tester.pumpWidget(const TaskBotApp());
    await tester.pumpAndSettle();

    expect(find.text('Task Bot'), findsOneWidget);
    expect(find.text('Bắt đầu'), findsOneWidget);
  });
}
