c='ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
m='ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
j=' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
#todo 예외사항 추가
def offset( chosung : str, moeum : str, jongseong : str):
    chosung=c.index(chosung)
    moeum=m.index(moeum)
    jongseong=j.index(jongseong)

    return chosung*588 + moeum*28 + jongseong + 44032
def Type(typeList: list, m : str,jongseong : str):
    jongseong=j.index(jongseong)
    for i in range(len(typeList)):
        if m in typeList[i]:
            if jongseong!=0:
                return i
            return i*100