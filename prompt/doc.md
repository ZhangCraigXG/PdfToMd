## 角色设定
你是一个python程序员，现在要研发一款python程序

## 程序说明
1.这款程序最终目标是将pdf文件（.pdf）转换成markdown文件（.md）
2.不需要web页面，在代码中手动指定源pdf文件路径和转换后的md文件保存路径，图片默认放在md文件保存路径下的img文件夹中
3.原pdf文件路径：/Users/craig/Downloads/个人设备.pdf
4.md文件保存路径：/Users/craig/Downloads/转换/个人设备.md
5.md图片保存路径：/Users/craig/Downloads/转换/img/
不要扩散需求，严格按照这个要求实现，最终只是实现将pdf转换成md


分析下这个项目，现在配置路径需要配置PDF_PATH、MD_OUTPUT_PATH、IMG_OUTPUT_DIR三个，并且只能指定一个pdf文件，现在我们的pdf文件变得更多了，如果每次都单独去设置pdf会变得非常麻烦，所以我们这里需要调整下需求，最终需要支持指定文件夹，具体要求如下：
1.当前有PDF_PATH、MD_OUTPUT_PATH、IMG_OUTPUT_DIR三个变量需要我们指定，现在只需要指定PDF_PATH，另外两个参数MD_OUTPUT_PATH、IMG_OUTPUT_DIR的逻辑如下：
MD_OUTPUT_PATH：这个是转换后的文件保存路径，它需要根据PDF_PATH选择的文件夹路径来设定，例如PDF_PATH = "/Users/craig/Downloads/test"，那么MD_OUTPUT_PATH="/Users/craig/Downloads/test_format"，也就是说MD_OUTPUT_PATH需要在PDF_PATH同级目录下创建一个“文件夹名_format”的目录用来保存转换后的文件
IMG_OUTPUT_DIR：这个是保存图片的路径，在穷举PDF_PATH目录下所有pdf文件的时候，如果某个目录下有pdf文件，那么就需要在test_format构建相同的路径，然后在这个路径下创建一个assets文件夹用来保存图片，例如：PDF_PATH = "/Users/craig/Downloads/test"这个文件夹的目录如下：
```
test
|	|--班级1
|	|	|--花名册1.pdf
|	|--班级2
|	|	|--花名册.pdf
|	|	|--活动
|	|	|	|--花名册2.pdf
```
那么转换后的路径则为：
```
test_format
|	|--班级1
|	|	|--assets
|	|	|--花名册1.md
|	|--班级2
|	|	|--assets
|	|	|--花名册.md
|	|	|--活动
|	|	|	|--assets
|	|	|	|--花名册2.md
```