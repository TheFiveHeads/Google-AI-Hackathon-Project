import 'package:flutter/material.dart';
import 'package:hackathonproject/form_Container_widget.dart';
import 'login.dart'; 
import 'main.dart';
class SignUp extends StatefulWidget {
  const SignUp({Key? key}) : super(key: key);

  @override
  SignUpState createState() => SignUpState();
}

class SignUpState extends State<SignUp> {
  TextEditingController usernameController = TextEditingController();
  TextEditingController emailController = TextEditingController();
  TextEditingController passwordController = TextEditingController();

  bool isSigningUp = false;

  @override
  void dispose() {
    usernameController.dispose();
    emailController.dispose();
    passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Homepage"),
        automaticallyImplyLeading: true,
      ),
      body: GestureDetector(
        onTap: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => HomePage()),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              SizedBox(height: 30),
              Text(
                "Create Account",
                style: TextStyle(fontSize: 40, fontWeight: FontWeight.bold, color: Colors.orange),
              ),
              SizedBox(height: 30),
              Text(
                "Fill in your credentials below",
                style: TextStyle(fontSize: 15, color: Colors.black),
              ),
              SizedBox(height: 5),
              FormContainerWidget(
                controller: usernameController,
                hintText: "Username",
                isPasswordField: false,
              ),
              SizedBox(height: 10),
              FormContainerWidget(
                controller: emailController,
                hintText: "Email",
                isPasswordField: false,
              ),
              SizedBox(height: 10),
              FormContainerWidget(
                controller: passwordController,
                hintText: "Password",
                isPasswordField: true,
              ),
              SizedBox(height: 30),
              GestureDetector(
                onTap: signUp,
                child: Container(
                  width: 150,
                  height: 40,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: Colors.orange),
                  ),
                  child: Center(
                    child: isSigningUp
                        ? CircularProgressIndicator(color: Colors.orange)
                        : Text(
                            "Sign Up",
                            style: TextStyle(
                              color: Colors.orange,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                  ),
                ),
              ),
              SizedBox(height: 10),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "Already have an account? ",
                    style: TextStyle(fontSize: 15, color: Colors.grey),
                  ),
                  Text(
                    "Login",
                    style: TextStyle(fontSize: 15, color: Colors.blue),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void signUp() async {
    setState(() {
      isSigningUp = true;
    });

    String username = usernameController.text;
    String email = emailController.text;
    String password = passwordController.text;

    setState(() {
      isSigningUp = false;
    });
  }
}
