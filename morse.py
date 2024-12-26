# -*- coding: utf-8 -*-
"""
@FilePath     : /Morsecode/main.py
@Author       : kunighting
@Date         : 2024-12-20 11:08:50
@LastEditTime : 2024-12-25 19:34:12
@Description  : 
"""
import time
import argparse
import itertools
import librosa
import numpy as np
import soundfile as sf

class MorsecodeTranslator:
    def __init__(self, codefile='./en.txt'):
        self.code_dict = {}
        self.read_morse_code(codefile)

    def read_morse_code(self,codefile:str)->None:
        """读取摩斯密码表（codefile）到字典中"""
        with open(codefile, 'r', encoding='utf-8') as f:
            # 跳过第一行
            f.readline()
            for line in f:
                code, word = line.split()
                self.code_dict[word] = code

    def morse_code(self, text:str)->str:
        """
        将文本转换为摩斯密码
        :param text: 待转换的文本
        :return -> str: 转换后的摩斯密码"""
        text = text.upper().split() # 转换为大写，并以空格隔开单词
        result = '' # 存储转换结果
        for  word in text:
            for char in word:
                if char in self.code_dict:
                    result += self.code_dict[char]
                else:
                    result += '?'
                result += ' '
            result = result.rstrip() # 去掉最后一个空格
            result += '/' # 加斜线隔开单词
        result = result.rstrip('/') # 去掉最后一个斜线    
        return result
    
    # 将摩斯密码转换为明文
    def decode_morse(self,morsecode:str)->str:
        """将摩斯密码转换为明文
        :param morsecode: 待转换的摩斯密码
        :return -> str: 转换后的明文"""
        morsecode = morsecode.replace('滴', '.').replace('哒', '-')
        morsecode = morsecode.replace('0', '.').replace('1', '-')
        if "//" in morsecode:
            morsecode = morsecode.replace('//', '/')
        # 将字典的键和值互换，将原字典的值作为新字典的键，原字典的键作为新字典的值
        new_dict = dict(zip(self.code_dict.values(), self.code_dict.keys()))
        result = '' # 存储转换结果
        for word in morsecode.split('/'):
            for code in word.split():
                if code in new_dict:
                    result += new_dict[code]
                else:
                    result += '?' # 未知的摩斯密码字符用问号代替
            result +=' ' # 加空格隔开单词
        return result
    
    # 输出摩斯密码转换结果到控制台
    def output_morsecode(self,str:str)->None:
        """输出摩斯密码转换结果到控制台
        :param str: 待输出的字符串(摩斯密码)
        :return -> None"""
        print(f"[result]: {str}")
        str_01 = str.replace('.', '0').replace('-', '1')
        str_02 = str.replace('.', '滴').replace('-', '哒')
        print(f"[result]: {str_01}")
        print(f"[result]: {str_02}")

    # 输出明文转换结果
    def plaintext_transfer(self, text:str)->None:
        """输出明文转换结果
        :param text: 待输出的字符串(明文)
        :return -> None"""
        print(f"[result] upper: {text}")
        print(f"[result] lower: {text.lower()}")
        print(f"[result] title: {text.title()}")
    
    # 将音频文件转换为摩斯密码
    def audio_to_morse(self, audiofile:str)->str:
        """分析音频文件，分析短时能量，识别其Morsecode
        :param audiofile: 音频文件路径
        :return -> str: 音频文件的Morsecode"""
        morsecode = '' # 存储音频的Morsecode
        
        # 读取音频文件
        y, sr = librosa.load(audiofile, sr=None, mono=True)
        # 计算音频的短时能量
        energy = librosa.feature.rms(y=y)[0]
        # 判断每个时间帧的短时能量是否大于0.1
        signal = energy > 0.1     # 序列的短时能量大于0.1为True，否则为False

        # 统计音频的每段短时能量大于0.1的时间帧数
        l_true = [len(list(group)) for key, group in itertools.groupby(signal) if key]
        # 统计音频的每段短时能量小于0.1的时间帧数
        l_false = [len(list(group)) for key, group in itertools.groupby(signal) if not key]

        # 为了更精确地识别音频的Morsecode，需要将短时能量小于0.1的时间帧数分成三段，划分成三个区间，对应点划的间隔，
        # 字母的间隔，单词的间隔。
        width = (max(l_false) - min(l_false))/3

        # 识别音频的Morsecode
        for key, group in itertools.groupby(signal):
            num = len(list(group))
            if key:
                if num < (max(l_true)+min(l_true))/2:
                    morsecode += '.'
                else:
                    morsecode += '-'
            else:
                if num < width:
                    morsecode += ''
                elif width < num < min(l_false) + 2*width:
                    morsecode += ' '
                else:
                    morsecode += '/'
        print(f"[info] morsecode: {morsecode}")
        return morsecode

    # 输出摩斯密码为音频文件
    def morse_to_audio(self, morsecode:str, audiofile:str)->None:
        """将摩斯密码转换为音频文件
        :param morsecode: 待转换的摩斯密码
        :param audiofile: 输出的音频文件路径
        :return -> None"""
        freq = 440  # 440Hz is the standard frequency of A
        dot_duration = 0.1  # duration of the tone in seconds
        dash_duration = 0.3  # duration of the tone in seconds
        sample_rate = 44100  # sample rate of the audio signal

        # 生成指定频率和持续时间的音调
        def generate_tone(freq, duration, sample_rate):
            """生成指定频率和持续时间的音调
            :param freq: 音调的频率
            :param duration: 音调持续的时间
            :param sample_rate: 采样率"""
            t = np.linspace(0, duration, int(duration * sample_rate))
            tone = np.sin(2 * np.pi * freq * t)
            return tone

        audio_data = []  # 存储音频数据
        dot_tone = generate_tone(freq, dot_duration, sample_rate)
        dash_tone = generate_tone(freq, dash_duration, sample_rate)
        silence = np.zeros(int(dot_duration * sample_rate))  # 每个点划间隔
        char_silence = np.zeros(int(3 * dot_duration * sample_rate)) # 每个字母间隔
        word_silence = np.zeros(int(7 * dot_duration * sample_rate)) # 每个单词间隔

        for char in morsecode:
            if char == ".":
                audio_data.append(dot_tone)
                audio_data.append(silence)
            elif char == "-":
                audio_data.append(dash_tone)
                audio_data.append(silence)
            elif char == " ":
                audio_data.pop()
                audio_data.append(char_silence)
            elif char == "/":
                audio_data.pop()
                audio_data.append(word_silence)

        audio_data = np.concatenate(audio_data)
        sf.write(audiofile, audio_data, sample_rate)

if __name__ == '__main__':
    # 创建参数解析器对象
    parser = argparse.ArgumentParser(description='Morsecode')
    group = parser.add_mutually_exclusive_group()
    # 添加选项参数
    group.add_argument('-e', '--encode', action='store_true', help='encode morsecode')
    group.add_argument('-d', '--decode', action='store_true', help='decode morsecode')
    group.add_argument('-da', '--decode_audio', action='store_true', help='decode the audio file')
    parser.add_argument('-o', '--output', action='store_true', help='output the morsecode as audio file')
    parser.add_argument('-f', '--file', type=str, help='specify the morsecodebook file', default='./en.txt')
    # 添加位置参数
    parser.add_argument('text', type=str, help='input text/or audio file path')
    # 解析参数
    args = parser.parse_args()

    # 获取参数值
    text = args.text
    
    # 创建MorsecodeTranslator对象
    translator = MorsecodeTranslator(args.file)
    
    # 加密/解密
    if args.encode:
        print("[info] encode morsecode")
        print("[info] 输出的摩斯密码以双斜线隔开单词，字母之间以空格隔开")
        print(f"[info] plaintext: {text}")
        morsecode = translator.morse_code(text)
        translator.output_morsecode(morsecode)
        if args.output:
            file_name = f"{int(time.time())}.wav"
            translator.morse_to_audio(morsecode, file_name)
            print(f"[info] output file: 当前路径/{file_name}")
    elif args.decode:
        print("[info] decode morsecode")
        print("[info] 输出的明文以空格隔开单词")
        print(f"[info] morsecode: {text}")
        plaintext = translator.decode_morse(text)
        translator.plaintext_transfer(plaintext)
    elif args.decode_audio:
        print("[info] decode audio file")
        print("[info] 输出的明文以空格隔开单词")
        print(f"[info] {args.text}")
        morsecode = translator.audio_to_morse(args.text)
        plaintext = translator.decode_morse(morsecode)
        translator.plaintext_transfer(plaintext)
       