import json
import os
import mysql.connector
from openai import OpenAI
from time import time

print("Running football_db_bot.py!")

fdir = os.path.dirname(__file__)

def getPath(fname):
    return os.path.join(fdir, fname)

setupSqlPath = getPath("setup.sql")

with open(setupSqlPath) as setupSqlFile:
    setupSqlScript = setupSqlFile.read()

mysqlCon = mysql.connector.connect(
    host="localhost",
    user="root",
    database="football_league"
)

mysqlCursor = mysqlCon.cursor()


def runSql(query):
    mysqlCursor.execute(query)
    result = mysqlCursor.fetchall()
    return result


# OPENAI
configPath = getPath("config.json")
print(configPath)
with open(configPath) as configFile:
    config = json.load(configFile)

openAiClient = OpenAI(api_key=config["openaiKey"])
chosen_model = "gpt-4o"


def getChatGptResponse(content):
    response = openAiClient.chat.completions.create(
        model=chosen_model,
        messages=[{"role": "user", "content": content}]
    )

    return response.choices[0].message.content


# PROMPTING STRATEGIES

commonSqlOnlyRequest = """
Give me a MySQL SELECT statement that answers the question.

Important database values:
- Quarterback is stored as 'QB'
- Running back is stored as 'RB'
- Wide receiver is stored as 'WR'
- Linebacker is stored as 'LB'
- Defensive end is stored as 'DE'
- Safety is stored as 'S'

Only respond with MySQL syntax.
Only generate SELECT queries.
Do not explain the query.
Do not modify the database.
"""


strategies = {
    "zero_shot":
        setupSqlScript +
        commonSqlOnlyRequest,

    "single_domain_double_shot":
        setupSqlScript +

        """
Question: Who plays quarterback for the Seattle Seahawks?

SELECT p.first_name, p.last_name
FROM player pl
JOIN person p ON pl.person_id = p.person_id
JOIN team t ON pl.team_id = t.team_id
WHERE pl.position = 'QB'
AND t.team_name = 'Seattle Seahawks';


Question: Which player has the most receiving yards?

SELECT p.first_name,
       p.last_name,
       SUM(os.receiving_yards) AS total_receiving_yards
FROM offensive_stats os
JOIN player pl ON os.player_id = pl.player_id
JOIN person p ON pl.person_id = p.person_id
GROUP BY p.person_id, p.first_name, p.last_name
ORDER BY total_receiving_yards DESC
LIMIT 1;

""" +
        commonSqlOnlyRequest
}


questions = [
    # "Who plays quarterback for the Seattle Seahawks?",
    # "Which player has the most receiving yards?",
    # "Who has the most rushing yards?",
    # "Which quarterback has thrown the most touchdowns?",
    # "Which player has the most sacks?",
    # "Who won the game between the Seahawks and Rams?",
    # "Which team scored the most points?",
    # "Where do the 49ers play their home games?",
    # "Who is the head coach of the Rams?",
    "How many touchdowns has the quarterback with the least amount of interceptions thrown?",
]


def sanitizeForJustSql(value):
    gptStartSqlMarker = "```"
    gptEndSqlMarker = "```"
    if gptStartSqlMarker in value:
        value = value.split(gptStartSqlMarker, 1)[1]
        newline_index = value.find("\n")
        if newline_index != -1:
            value = value[newline_index + 1:]
    if gptEndSqlMarker in value:
        value = value.split(gptEndSqlMarker, 1)[0]
    return value.strip()


for strategy in strategies:
    responses = {"strategy": strategy,"prompt_prefix": strategies[strategy]}
    questionResults = []
    print("########################################################################")
    print(f"Running strategy: {strategy}")
    for question in questions:
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Question:")
        print(question)
        sqlSyntaxResponse = ""
        queryRawResponse = ""
        friendlyResponse = ""
        error = "None"

        try:
            prompt = strategies[strategy] + "\nQuestion: " + question
            sqlSyntaxResponse = getChatGptResponse(prompt)
            sqlSyntaxResponse = sanitizeForJustSql(sqlSyntaxResponse)

            print("\nSQL Syntax Response:")
            print(sqlSyntaxResponse)

            if not sqlSyntaxResponse.strip().upper().startswith(("SELECT", "WITH")):
                raise ValueError("Only SELECT queries are allowed.")

            queryRawResponse = str(runSql(sqlSyntaxResponse))
            print("\nQuery Raw Response:")
            print(queryRawResponse)

            friendlyResultsPrompt = f"""
            The user asked:

            "{question}"

            The SQL query used was:

            {sqlSyntaxResponse}

            The database returned:

            {queryRawResponse}

            Answer the user's original question in a concise and friendly way.
            Only use information contained in the database results.
            Do not provide suggestions or additional information.
            """

            friendlyResponse = getChatGptResponse(friendlyResultsPrompt)
            print("\nFriendly Response:")
            print(friendlyResponse)

        except Exception as err:
            error = str(err)
            print("\nError:")
            print(err)

        questionResults.append({
            "question": question,
            "sql": sqlSyntaxResponse,
            "queryRawResponse": queryRawResponse,
            "friendlyResponse": friendlyResponse,
            "error": error
        })

    responses["questionResults"] = questionResults

    with open( getPath(f"response_{strategy}_{time()}.json"),"w") as outFile:
        json.dump( responses, outFile, indent=2)

mysqlCursor.close()
mysqlCon.close()
print("Done!")