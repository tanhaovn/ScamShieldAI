import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';

const defaultApiBase = String.fromEnvironment(
  'API_BASE',
  defaultValue: 'http://10.0.2.2:8000',
);

void main() {
  runApp(const ScamDetectorApp());
}

class ScamDetectorApp extends StatelessWidget {
  const ScamDetectorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Scam Detector',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xffef7d5c),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xfff5f8f4),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.white,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xffd9e6df)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: Color(0xffd9e6df)),
          ),
        ),
      ),
      home: const AuthGate(),
    );
  }
}

class ApiService {
  ApiService(this.baseUrl, {this.token});

  final String baseUrl;
  final String? token;

  Map<String, String> get headers => {
        if (token != null && token!.isNotEmpty) 'Authorization': 'Bearer $token',
      };

  Future<http.Response> postJson(String path, Map<String, dynamic> body) {
    return http.post(
      Uri.parse('$baseUrl$path'),
      headers: {'Content-Type': 'application/json', ...headers},
      body: jsonEncode(body),
    );
  }

  Future<List<dynamic>> getList(String path) async {
    final response = await http.get(Uri.parse('$baseUrl$path'), headers: headers);
    if (response.statusCode >= 400) {
      throw Exception(_error(response));
    }
    return jsonDecode(response.body) as List<dynamic>;
  }

  Future<Map<String, dynamic>> scan(XFile image, {int? categoryId}) async {
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/check-image'));
    request.headers.addAll(headers);
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      await image.readAsBytes(),
      filename: image.name,
    ));
    if (categoryId != null) {
      request.fields['scam_category_id'] = '$categoryId';
    }
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    if (response.statusCode >= 400) {
      throw Exception(_error(response));
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  String _error(http.Response response) {
    try {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return body['detail']?.toString() ?? 'Có lỗi từ backend (${response.statusCode})';
    } catch (_) {
      return 'Không kết nối được backend (${response.statusCode})';
    }
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  String? token;
  Map<String, dynamic>? user;

  @override
  void initState() {
    super.initState();
    _restoreSession();
  }

  Future<void> _restoreSession() async {
    final prefs = await SharedPreferences.getInstance();
    final savedToken = prefs.getString('token');
    final savedUser = prefs.getString('user');
    if (!mounted) return;
    setState(() {
      token = savedToken;
      user = savedUser == null ? null : jsonDecode(savedUser) as Map<String, dynamic>;
    });
  }

  Future<void> _onAuthenticated(String newToken, Map<String, dynamic> newUser) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', newToken);
    await prefs.setString('user', jsonEncode(newUser));
    if (!mounted) return;
    setState(() {
      token = newToken;
      user = newUser;
    });
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('user');
    if (!mounted) return;
    setState(() {
      token = null;
      user = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (token == null) {
      return AuthPage(onAuthenticated: _onAuthenticated);
    }
    return HomePage(token: token!, user: user ?? {}, onLogout: _logout);
  }
}

class AuthPage extends StatefulWidget {
  const AuthPage({super.key, required this.onAuthenticated});

  final Future<void> Function(String token, Map<String, dynamic> user) onAuthenticated;

  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();
  final nameController = TextEditingController();
  bool register = false;
  bool loading = false;

  Future<void> submit() async {
    if (emailController.text.trim().isEmpty || passwordController.text.isEmpty) {
      _show('Vui lòng nhập email và mật khẩu');
      return;
    }
    setState(() => loading = true);
    try {
      final api = ApiService(defaultApiBase);
      final response = await api.postJson(
        register ? '/register' : '/login',
        {
          'email': emailController.text.trim(),
          'password': passwordController.text,
          if (register) 'full_name': nameController.text.trim(),
        },
      );
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode >= 400) throw Exception(body['detail'] ?? 'Xác thực thất bại');
      await widget.onAuthenticated(body['token'] as String, body['user'] as Map<String, dynamic>);
    } catch (error) {
      _show(error.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  void _show(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Card(
                elevation: 0,
                color: Colors.white.withValues(alpha: .9),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      const Icon(Icons.verified_user_outlined, size: 52, color: Color(0xffef7d5c)),
                      const SizedBox(height: 12),
                      Text('Scam Detector', textAlign: TextAlign.center, style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w800, color: const Color(0xff123e43))),
                      const SizedBox(height: 6),
                      const Text('Kiểm tra trước khi bạn tin', textAlign: TextAlign.center, style: TextStyle(color: Color(0xff69817b))),
                      const SizedBox(height: 24),
                      SegmentedButton<bool>(
                        segments: const [
                          ButtonSegment(value: false, label: Text('Đăng nhập')),
                          ButtonSegment(value: true, label: Text('Đăng ký')),
                        ],
                        selected: {register},
                        onSelectionChanged: (value) => setState(() => register = value.first),
                      ),
                      const SizedBox(height: 18),
                      if (register) ...[
                        TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Họ và tên', prefixIcon: Icon(Icons.person_outline))),
                        const SizedBox(height: 12),
                      ],
                      TextField(controller: emailController, keyboardType: TextInputType.emailAddress, decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined))),
                      const SizedBox(height: 12),
                      TextField(controller: passwordController, obscureText: true, decoration: const InputDecoration(labelText: 'Mật khẩu', prefixIcon: Icon(Icons.lock_outline))),
                      const SizedBox(height: 18),
                      FilledButton.icon(onPressed: loading ? null : submit, icon: loading ? const SizedBox.square(dimension: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.arrow_forward), label: Text(register ? 'Tạo tài khoản' : 'Vào ứng dụng')),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.token, required this.user, required this.onLogout});

  final String token;
  final Map<String, dynamic> user;
  final Future<void> Function() onLogout;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final picker = ImagePicker();
  late final ApiService api;
  List<dynamic> categories = [];
  List<dynamic> history = [];
  XFile? selectedImage;
  Map<String, dynamic>? result;
  int? selectedCategory;
  int tab = 0;
  bool loading = false;

  @override
  void initState() {
    super.initState();
    api = ApiService(defaultApiBase, token: widget.token);
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final values = await Future.wait([
        api.getList('/scam-categories'),
        api.getList('/scan-history'),
      ]);
      if (!mounted) return;
      setState(() {
        categories = values[0];
        history = values[1];
        if (categories.isNotEmpty) selectedCategory = categories.first['id'] as int;
      });
    } catch (error) {
      _show(error.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> chooseImage(ImageSource source) async {
    final picked = await picker.pickImage(source: source, imageQuality: 90);
    if (picked == null) return;
    setState(() {
      selectedImage = picked;
      result = null;
    });
  }

  Future<void> scan() async {
    if (selectedImage == null) {
      _show('Hãy chọn ảnh hoặc chụp ảnh trước');
      return;
    }
    setState(() => loading = true);
    try {
      final data = await api.scan(selectedImage!, categoryId: selectedCategory);
      if (!mounted) return;
      setState(() => result = data);
      final updated = await api.getList('/scan-history');
      if (mounted) setState(() => history = updated);
    } catch (error) {
      _show(error.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  void _show(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scam Detector', style: TextStyle(fontWeight: FontWeight.w800)),
        actions: [IconButton(onPressed: widget.onLogout, tooltip: 'Đăng xuất', icon: const Icon(Icons.logout))],
      ),
      body: IndexedStack(index: tab, children: [_scanView(), _historyView()]),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        onDestinationSelected: (value) => setState(() => tab = value),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.document_scanner_outlined), selectedIcon: Icon(Icons.document_scanner), label: 'Kiểm tra'),
          NavigationDestination(icon: Icon(Icons.history_outlined), selectedIcon: Icon(Icons.history), label: 'Lịch sử'),
        ],
      ),
    );
  }

  Widget _scanView() {
    final displayName = widget.user['full_name'] ?? widget.user['email'] ?? 'bạn';
    return RefreshIndicator(
      onRefresh: _loadData,
      child: ListView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        children: [
          Text('Xin chào, $displayName', style: Theme.of(context).textTheme.titleMedium?.copyWith(color: const Color(0xff69817b))),
          const SizedBox(height: 6),
          Text('Một bước kiểm tra trước khi chuyển tiền.', style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800, color: const Color(0xff123e43))),
          const SizedBox(height: 18),
          Card(
            elevation: 0,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  _imagePreview(),
                  const SizedBox(height: 14),
                  Row(children: [Expanded(child: OutlinedButton.icon(onPressed: () => chooseImage(ImageSource.gallery), icon: const Icon(Icons.photo_library_outlined), label: const Text('Thư viện'))), const SizedBox(width: 10), Expanded(child: OutlinedButton.icon(onPressed: () => chooseImage(ImageSource.camera), icon: const Icon(Icons.camera_alt_outlined), label: const Text('Chụp ảnh')))]),
                  const SizedBox(height: 14),
                  DropdownButtonFormField<int>(value: selectedCategory, decoration: const InputDecoration(labelText: 'Loại kiểm tra'), items: categories.map((category) => DropdownMenuItem<int>(value: category['id'] as int, child: Text(category['display_name'].toString()))).toList(), onChanged: (value) => setState(() => selectedCategory = value)),
                  const SizedBox(height: 14),
                  FilledButton.icon(onPressed: loading ? null : scan, icon: loading ? const SizedBox.square(dimension: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.search), label: Text(loading ? 'Đang phân tích...' : 'Phân tích ảnh')),
                ],
              ),
            ),
          ),
          if (result != null) ...[
            const SizedBox(height: 16),
            _resultCard(),
          ],
        ],
      ),
    );
  }

  Widget _imagePreview() {
    if (selectedImage == null) {
      return Container(
        height: 190,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: const Color(0xfff1f8f3),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xffa9c9bd)),
        ),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.image_search_outlined, size: 46, color: Color(0xff4c9b8e)),
            SizedBox(height: 8),
            Text('Chọn ảnh màn hình, tin nhắn hoặc hóa đơn'),
          ],
        ),
      );
    }
    return FutureBuilder<Uint8List>(
      future: selectedImage!.readAsBytes(),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const SizedBox(height: 240, child: Center(child: CircularProgressIndicator()));
        }
        return ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: Image.memory(snapshot.data!, height: 240, fit: BoxFit.cover),
        );
      },
    );
  }

  Widget _resultCard() {
    final score = (result!['risk_score'] as num?)?.toInt() ?? 0;
    final dangerous = score >= 60;
    final suspicious = score >= 25;
    final color = dangerous ? Colors.red : suspicious ? Colors.orange : Colors.green;
    return Card(
      elevation: 0,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Kết quả phân tích', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
            const SizedBox(height: 14),
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: color.withValues(alpha: .13),
                  child: Text('$score', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 20, color: color)),
                ),
                const SizedBox(width: 14),
                Expanded(child: Text(dangerous ? 'Nguy hiểm' : suspicious ? 'Nghi ngờ' : 'An toàn', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: color))),
              ],
            ),
            const SizedBox(height: 14),
            Text(result!['explanation']?.toString() ?? 'Chưa có giải thích.'),
            const SizedBox(height: 10),
            Text('Đề xuất: ${result!['suggested_action'] ?? 'Cẩn thận với giao dịch này.'}', style: const TextStyle(fontWeight: FontWeight.w700)),
          ],
        ),
      ),
    );
  }

  Widget _historyView() {
    return RefreshIndicator(onRefresh: _loadData, child: history.isEmpty ? ListView(children: const [SizedBox(height: 220), Center(child: Text('Chưa có lịch sử kiểm tra'))]) : ListView.separated(padding: const EdgeInsets.all(16), itemCount: history.length, separatorBuilder: (_, __) => const SizedBox(height: 10), itemBuilder: (_, index) {
      final item = history[index] as Map<String, dynamic>;
      final score = (item['risk_score'] as num?)?.toInt() ?? 0;
      final color = score >= 60 ? Colors.red : score >= 25 ? Colors.orange : Colors.green;
      return Card(elevation: 0, child: ListTile(leading: CircleAvatar(backgroundColor: color.withValues(alpha: .13), child: Text('$score', style: TextStyle(color: color, fontWeight: FontWeight.w800))), title: Text(item['original_filename']?.toString() ?? 'Ảnh đã kiểm tra', maxLines: 1, overflow: TextOverflow.ellipsis), subtitle: Text(item['risk_level']?.toString() ?? 'Chưa phân loại'), trailing: const Icon(Icons.chevron_right)));
    }));
  }
}
