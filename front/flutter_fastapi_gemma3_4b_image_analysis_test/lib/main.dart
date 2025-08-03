import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path; // Alias the path import

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Receipt Analyzer',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: ReceiptAnalyzerScreen(),
    );
  }
}

class ReceiptAnalyzerScreen extends StatefulWidget {
  @override
  _ReceiptAnalyzerScreenState createState() => _ReceiptAnalyzerScreenState();
}

class _ReceiptAnalyzerScreenState extends State<ReceiptAnalyzerScreen> {
  File? _image;
  String _date = '';
  String _total = '';

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _date = '';
        _total = '';
      });
    }
  }

  Future<void> _uploadImage() async {
    if (_image == null) return;

    final uri = Uri.parse("http://localhost:8000/analyze_receipt");

    final request = http.MultipartRequest('POST', uri);
    request.files.add(
      await http.MultipartFile.fromPath(
        'file',
        _image!.path,
        filename: path.basename(_image!.path),
      ),
    );

    try {
      final response = await request.send();

      if (response.statusCode == 200) {
        final responseData = await response.stream.bytesToString();
        final jsonData = jsonDecode(responseData);
        if (!mounted) return;
        setState(() {
          _date = jsonData['date'];
          _total = jsonData['total'];
        });
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('분석 성공')));
      } else {
        if (!mounted) return;
        setState(() {
          _date = '분석 실패';
          _total = '분석 실패';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('분석 실패: ${response.statusCode}')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _date = '연결 오류';
        _total = '연결 오류';
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('연결 오류: $e')));
      print('Error details: $e'); // 콘솔에 상세 로그 출력
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('영수증 분석')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _image != null
                ? Image.file(_image!, width: 200)
                : Text('영수증 이미지를 선택해주세요'),
            const SizedBox(height: 20),
            Text('날짜: $_date'),
            Text('합계: $_total'),
            const SizedBox(height: 20),
            ElevatedButton(onPressed: _pickImage, child: Text('이미지 선택')),
            const SizedBox(height: 10),
            ElevatedButton(onPressed: _uploadImage, child: Text('분석 요청')),
          ],
        ),
      ),
    );
  }
}
