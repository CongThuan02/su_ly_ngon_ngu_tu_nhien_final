import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'services/api_service.dart';
import 'providers/chat_provider.dart';
import 'providers/task_provider.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const TaskBotApp());
}

class TaskBotApp extends StatelessWidget {
  const TaskBotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Task Bot',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
        brightness: Brightness.light,
      ),
      darkTheme: ThemeData(
        colorSchemeSeed: Colors.blue,
        useMaterial3: true,
        brightness: Brightness.dark,
      ),
      themeMode: ThemeMode.system,
      home: const _AppStartup(),
      routes: {
        '/login': (_) => const LoginScreen(),
        '/home': (_) => const _AppWithProviders(),
      },
    );
  }
}

class _AppStartup extends StatelessWidget {
  const _AppStartup();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<SharedPreferences>(
      future: SharedPreferences.getInstance(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        final userName = snapshot.data!.getString('user_name');
        if (userName == null) {
          return const LoginScreen();
        }
        return const _AppWithProviders();
      },
    );
  }
}

class _AppWithProviders extends StatelessWidget {
  const _AppWithProviders();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<SharedPreferences>(
      future: SharedPreferences.getInstance(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const Scaffold(body: Center(child: CircularProgressIndicator()));
        }

        final userId = snapshot.data!.getString('user_id') ?? 'default';
        final api = ApiService();

        return MultiProvider(
          providers: [
            ChangeNotifierProvider(
              create: (_) => ChatProvider(api: api, userId: userId),
            ),
            ChangeNotifierProvider(
              create: (_) => TaskProvider(api: api, userId: userId),
            ),
          ],
          child: const HomeScreen(),
        );
      },
    );
  }
}
