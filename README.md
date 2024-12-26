# Morsecode

一个简单的摩斯密码翻译器。
用"."和"-"，"0"和"1", "滴"和"哒"表示

## 功能
- 可以根据密码表来翻译摩斯密码，默认使用英文密码表。
- 加密：将文本转换为摩斯密码（文本格式以及声音格式）。
- 解密：将摩斯密码（文本格式以及声音格式）转换为文本。

## 依赖
- Python 3.x
- numpy,soundfile,librosa

## 使用方法
```
# 编码
python morsecode.py -e "Hello world!"
# 编码并输出wav,以时间戳命名
python morse.py -e "Hello world" -o
# 解码
python morsecode.py -d ".... . .-.. .-.. ---   .-- --- .-. .-.. -.. -.-.--"
# 从音频中解码
python morsecode.py -da sound.wav
```



## 参考资料
- [维基百科-摩斯密码](https://zh.wikipedia.org/wiki/%E6%91%A9%E6%96%AF%E5%AF%86%E7%A0%81)
