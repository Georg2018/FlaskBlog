## A Simple Example Blog Implemented by Flask

This is a simple personal Blog that implemented by Flask web framework. It has some basic features of a blog like loggin, logout, follow, permission control, avatar, etc. It also has a azure blue theme.

I also sincerely hope that it would help you.

The blog hasn't been completed yet. I will add more functionalities in the future.

Todo:

- [x] Tags.
- [x] Api.
- [ ] Third party login.
- [x] Search.

---
Simple Usage:
1. Use the `pipenv install` or `pip install -r requirements.txt` command to install the dependencies.
2. Add a environment variable named `FLASK_APP` which value is equal to this blog's directory path.
3. Execute the `flask create` command in your command line environment.

---
Generate Fake Data:
1. Once you done the above work, you can use `flask fake_user`, `flask fake_post`, `flask fake_comment` to generate the fake data to test.

---
Demo site:

[Demo](http://101.132.174.76:3939/)

---
Previewing the interface:

![](http://arian-blogs.oss-cn-beijing.aliyuncs.com/18-4-26/24559028.jpg)
