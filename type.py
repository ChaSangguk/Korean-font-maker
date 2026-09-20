class Type:
    c='ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    m='ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
    j=' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    def __init__(self):
        pass

    def getType(self, typeList: list, m : str,jongseong : str):
        j_index =self.j.index(jongseong)
        for i in range(len(typeList)):
            if m in typeList[i]:
                if j_index != 0:
                    return i
        return -1
    def 