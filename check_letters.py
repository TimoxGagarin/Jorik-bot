abc = {
    'а':0,
    'б':1,
    'в':2,
    'г':3,
    'д':4,
    'е':5,
    'ё':5,
    'ж':6,
    'з':7,
    'и':8,
    'й':8,
    'к':9,
    'л':10,
    'м':11,
    'н':12,
    'о':13,
    'п':14,
    'р':15,
    'с':16,
    'т':17,
    'у':18,
    'ф':19,
    'х':20,
    'ц':21,
    'ч':22,
    'ш':23,
    'щ':23,
    'ъ':24,
    'ы':25,
    'ь':24,
    'э':26,
    'ю':27,
    'я':28,
}

letters_variants = [
    ['a', 'а'],
    ['б', '6', 'b'],
    ['в', 'w', 'v', '8'],
    ['г', 'g', 'r'],
    ['д', '9', 'q', 'g', 'd'],
    ['е', 'ё', 'e'],
    ['ж', 'j'],
    ['з', 'z', '3'],
    ['и', 'i', '1', 'l', 'й', 'u'],
    ['к', 'k'],
    ['л', 'l'],
    ['м', 'm'],
    ['н', 'n', 'h'],
    ['о', 'o', '0'],
    ['п', 'p'],
    ['р', 'p'],
    ['с', 'c', 's'],
    ['т', 't'],
    ['у', 'у', 'u'],
    ['ф', 'f'],
    ['х', 'x'],
    ['ц', 'c'],
    ['ч', '4'],
    ['ш', 'щ'],
    ['ь', 'ъ', '6'],
    ['э', 'е', 'ё', 'e'],
    ['ю', 'u'],
    ['я', 'r']
]

def check_msg4bad_words():
    if message.status < 4 and message.user_id != -GROUP_ID:
        [add_pred_and_check(message.user_id) if word in bad_words else None for word in message.text_low.split(' ')]
        for word in message.text_low.split(' '):
            pass

