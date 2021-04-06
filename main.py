import random
import time
import en_core_web_lg
import nltk
import sqlite3
import re
import warnings
from nltk import WordNetLemmatizer

start_time_program = time.time()
training_pattern = []
training_keyword = []
training_general_keyword = []

nlp = en_core_web_lg.load()
warnings.simplefilter("error", UserWarning)

# open database connection, and make a cursor
connection = sqlite3.connect('CAPEsDatabase (1).db')
cursor = connection.cursor()

random = random.randint(0, 10000)
counter = 0
gk = 0.0
gkc = 0.0
rk = 0.0
rkc = 0.0
rs = 0.0
rsc = 0.0
l = 0.0
lc = 0.0
p = 0.0
pc = 0.0
k = 0.0
kc = 0.0
gn = 0.0
gnc = 0.0
ps = 0.0
psc = 0.0
q = 0.0
qc = 0.0


# exit the chat
def exitProgram(x):
    if x == 'q':
        print("CAPES: conversation ends. Your records are saved in logs.")
        exit()


# 1. find keyword
# 1.2 get the keywords from database and compare them with user input
# V2: handle typos
def getKeyword(user_input):
    global gk, gkc
    # start_time = time.time()
    # lemmatize the user input first, I cannot call it bc it's calls other methods
    user_input_tokenized = user_input.split()
    user_input_list = list(user_input_tokenized)

    # sql query to get keywords, add the result in a list، change query upon user_input
    cursor.execute("SELECT keyword FROM keyword")
    keywords_list = [i[0] for i in cursor.fetchall()]

    # find the intersection between user input list and keywords list
    list_matching = list(set(user_input_list).intersection(set(keywords_list)))
    # end_time = time.time()
    # gk += (end_time - start_time)
    # gkc += 1
    # print("getKeyword() execution time:", end_time - start_time)
    return list_matching

    """# find the intersection between user input list and keywords list
    list_matching = list(set(user_input_list).intersection(set(keywords_list)))
    return list_matching"""


# 2. find pattern similarity (3 steps for cleaning)
# 2.1 remove keywords from user input
def removeKey(user_input):
    global rk, rkc
    # start_time = time.time()
    keywords = getKeyword(user_input)
    removed_keyword = ' '.join(word for word in user_input.split() if word not in keywords)
    # end_time = time.time()
    # rk += (end_time - start_time)
    # rkc += 1
    # print("removeKey() execution time:", end_time - start_time)
    return removed_keyword


# 2.2 remove special characters from user input
def removeSpecialCharacters(user_input):
    global rs, rsc
    # start_time = time.time()
    patterns = r'[^a-zA-z0-9\s]'  # what does it mean??
    user_input_removed_char = re.sub(patterns, '', user_input)
    # end_time = time.time()
    # rs += (end_time - start_time)
    # rsc += 1
    # print("removeSpecialCharacters() execution time:", end_time - start_time)
    return user_input_removed_char


# 2.3 lemmatize user input, make each word back to root
def lemmatize(user_input):
    global l, lc
    # start_time = time.time()
    lemmatizer = WordNetLemmatizer()
    user_input_lemmatized = ' '.join(lemmatizer.lemmatize(w) for w in nltk.word_tokenize(user_input))
    # end_time = time.time()
    # l += (end_time - start_time)
    # lc += 1
    # print("lemmatize() execution time:", end_time - start_time)
    return user_input_lemmatized


# 2.4 get the patterns from database and compare them with user input, get the most matching pattern similarity -
# only to save it in logs-
# we should lemmatize pattern in the database
def pattern(query):
    global p, pc
    # start_time = time.time()
    cursor.execute("SELECT anwser_p FROM pattern Where id_r = ?", [query])
    patterns = cursor.fetchall()
    for row in patterns:
        training_pattern.append(row[0])

    # end_time = time.time()
    # p += (end_time - start_time)
    # pc += 1
    # print("pattern() execution time:", end_time - start_time)
    return training_pattern


def keyword(user_input, query):
    global k, kc
    # start_time = time.time()
    user_input_tokenized = user_input.split()
    user_input_list = list(user_input_tokenized)

    cursor.execute("SELECT keyword FROM keyword Where id_r = ?", [query])
    patterns = cursor.fetchall()

    for row in patterns:
        training_keyword.append(row[0])
    list_matching = list(set(user_input_list).intersection(set(training_keyword)))
    # end_time = time.time()
    # k += (end_time - start_time)
    # kc += 1
    # print("keyword() execution time:", end_time - start_time)
    return list_matching


def generalKeyword(user_input, query):
    global gn, gnc
    # start_time = time.time()
    user_input_tokenized = user_input.split()
    user_input_list = list(user_input_tokenized)

    cursor.execute("SELECT keyword FROM keyword Where id_c = ?", [query])
    result = cursor.fetchall()

    for row in result:
        training_general_keyword.append(row[0])
    list_matching = list(set(user_input_list).intersection(set(training_general_keyword)))

    # end_time = time.time()
    # gn += (end_time - start_time)
    # gnc += 1
    # print("generalKeyword() execution time:", end_time - start_time)
    return list_matching


def patternSimilarity(user_input):
    global ps, psc
    # start_time = time.time()
    # user_input_cleaned = lemmatize(removeSpecialCharacters(removeKey(user_input)))
    user = removeSpecialCharacters(user_input)
    user_cleaned = lemmatize(user)
    user_input_cleaned = removeKey(user_cleaned)

    similarity_list = []

    if len(user_input_cleaned) > 0:
        token1 = nlp(user_input_cleaned)
        for row in training_pattern:
            token2 = nlp(row)
            try:
                similarity = token1.similarity(token2)
            except UserWarning:
                similarity = 0.0
            similarity_list.append(similarity)
        # end_time = time.time()
        # print("keyword() execution time:", end_time - start_time)
        return max(similarity_list)
    else:
        token1 = nlp(user_input)
        for row in training_keyword:
            token2 = nlp(row)
            try:
                similarity = token1.similarity(token2)
            except UserWarning:
                similarity = 0.0
            similarity_list.append(similarity)
        # end_time = time.time()
        # ps += (end_time - start_time)
        # psc += 1
        # print("patternSimilarity() execution time:", end_time - start_time)
        return max(similarity_list)


def question(count):
    global q, qc
    if count > 5:
        findCertificate()
        exit()

    else:
        cursor.execute("SELECT question FROM questions")
        question_result = [i[0] for i in cursor.fetchall()]
        questions = ''.join(question_result[count])  # loop over questions table, and save the result in questions

        user_input = input(questions).lower()

        # user_inputs = ['cs', 'level 1', 'database', 'no', 'c#', 'no', 'long']
        # user_inputs = ['CS', '6', 'OOP', 'no', 'Java', 'Oracle', 'Long term']
        # user_inputs = ['CS', '6', 'AI', 'no', 'python', 'oracle', 'short term']
        # user_inputs = ['CS', 'Level 6', 'OOP', 'no', 'Java', 'no', 'Short term']
        # user_inputs = ['CS', 'level 6', 'Oop', 'no', 'C++', 'no', 'Short term']
        # user_inputs = ['CS', '10', 'no', 'no', 'Java', 'no', 'Short term']
        # user_inputs = ['cs', 'level 1', 'database', 'no', 'c#', 'no', 'long']
        # user_input = ''.join(user_inputs[count]).lower()

        exitProgram(user_input)
        pattern(count + 1)
        keyword1 = keyword(user_input, count + 1)

        # 2 is general, 3 is weather, 4 is rude
        general = generalKeyword(user_input, 2)
        weather = generalKeyword(user_input, 3)
        rude = generalKeyword(user_input, 4)

        # if the user input has keyword/s then check the similarity, if not check for other keywords
        if len(keyword1) != 0:
            if patternSimilarity(user_input) > 0.7:
                # only used to upload log
                pattern_similarity = patternSimilarity(user_input)
                keywords = " ".join(getKeyword(user_input))
                user_input_removed_keywords = "".join(removeKey(user_input))

                # solve this, add more
                if user_input == "no":
                    keywords = None

                # insert into Logs
                data = (random, user_input, user_input_removed_keywords, keywords, pattern_similarity, questions)
                cursor.execute(
                    "INSERT INTO log (qNumer, userAns, textWithOutKey, keywords , patternAsimilarity, question) "
                    "VALUES (?, ?, ?, ?, ?, ?)", data)
                connection.commit()

                training_keyword.clear()
                training_pattern.clear()
                question((count + 1))

            else:
                print("Sorry, no similarity.")
                question(count)

        elif len(general) != 0:
            print("This is general", general)
            question(count)

        elif len(weather) != 0:
            print("This is weather", weather)
            question(count)

        elif len(rude) != 0:  # in keywords table it may contain only one word, not two
            print("This is rude", rude)
            question(count)
        else:
            print("Sorry,no matching")  # i should rewrite the msg to indicate the user didn't enter a string
            question(count)

    return count


# 3. find certificate
def findCertificate():
    # start_time = time.time()
    cursor.execute("SELECT keywords FROM log WHERE qNumer=?", [random])
    result = cursor.fetchall()
    key_list = []

    for row in result:
        key_list.append(row[0])
    cursor.execute("SELECT name  FROM certificate WHERE (major =? AND level =? AND field =? "
                   "AND prog_l =? AND v_username =? AND duration=?)",
                   (key_list[0], key_list[1], key_list[2], key_list[3], key_list[4], key_list[5]))
    # cursor.execute("SELECT name  FROM certificate WHERE (major =? AND level =? AND field =? AND "
    #                "pre_c =? AND prog_l =? AND v_username =? AND duration=?)",
    #                (key_list[0], key_list[1], key_list[2], key_list[3], key_list[4], key_list[5], key_list[6]))
    # cursor.execute("SELECT name  FROM certificate WHERE (level =? AND field =?)",
    #                (key_list[1], key_list[2]))
    results = cursor.fetchall()

    print("CAPEs: I found the most matching certificate for you: ")
    for row in results:
        print("-", row[0])
        # end_time = time.time()
    # print("findCertificate() execution time:", end_time - start_time)
    # print("\nProgram execution time:", end_time - start_time_program)


question(counter)

"""start_time = time.time()
question(counter)
end_time = time.time()

q += (end_time - start_time)
qc += 1
print("question() execution time:", end_time - start_time, q, q / qc)

print("getKeyword() execution time:", gkc, gk / gkc)
print("removeKey() execution time:", rkc, rk / rkc)
print("removeSpecialCharacters() execution time:", rsc, rs / rsc)
print("lemmatize() execution time:", lc, l / lc)
print("pattern() execution time:", pc, p / pc)
print("keyword() execution time:", kc, k / kc)
print("generalKeyword() execution time:", gnc, gn / gnc)
print("patternSimilarity() execution time:", psc, ps / psc)
"""