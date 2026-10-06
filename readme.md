# AI SQL Project

## Project Description
My project models a database that can be used to manage a football league, it includes information on people (coaches and players), teams, games, and stats.

## Working Code
[AI-SQL GitHub Repository](https://github.com/LukeChamberlain/AI-SQL/tree/main)

## Database Schema
[View the Football League Database Schema](football_database_schema.pdf)

## Example of Zero-shot vs Double Shot
One of my favorite examples was:
> **How many touchdowns has the quarterback with the least amount of interceptions thrown?**
This example was interesting because the **zero-shot strategy returned an incorrect answer**, while the **single-domain double-shot strategy returned the correct answer**.

### Zero-Shot Strategy
The zero-shot strategy generated the following SQL:
```sql
SELECT p.first_name, p.last_name, SUM(o.touchdowns) AS total_touchdowns
FROM offensive_stats o
JOIN player pl ON o.player_id = pl.player_id
JOIN person p ON pl.person_id = p.person_id
WHERE pl.position = 'QB'
GROUP BY o.player_id
ORDER BY MIN(o.interceptions) ASC
LIMIT 1;
```

The problem is this line:
```sql
ORDER BY MIN(o.interceptions) ASC
```

This is incorrect because this gets the smallest amount of interceptions in a game which happened for multiple quarterbacks so this is not an accurate way of retrieving the information for "How many touchdowns has the quarterback with the least amount of interceptions thrown?"

The query returned:
```text
[('Sam', 'Darnold', Decimal('7'))]
```

Response was:
> The quarterback with the least amount of interceptions, Sam Darnold, has thrown 7 touchdowns.

### Double-Shot Strategy

The double-shot strategy generated:
```sql
SELECT p.first_name,
       p.last_name,
       SUM(os.touchdowns) AS total_touchdowns
FROM offensive_stats os
JOIN player pl ON os.player_id = pl.player_id
JOIN person p ON pl.person_id = p.person_id
WHERE pl.position = 'QB'
GROUP BY p.person_id
ORDER BY SUM(os.interceptions) ASC
LIMIT 1;
```

The important difference is:
```sql
ORDER BY SUM(os.interceptions) ASC
```

Instead of finding the minimum interceptions from a single game, this query adds together all of each quarterback's interceptions and then finds the quarterback with the lowest total across all games.

The query returned:
```text
[('Brock', 'Purdy', Decimal('7'))]
```

Response was:
> Brock Purdy is the quarterback with the least amount of interceptions, and he has thrown 7 touchdowns.

## Zero-shot vs double-shot comparison

**zero-shot:** Chat-GPT was given the database schema and the question thats all.

**double-shot:**Chat-GPT was given the database schema, question, and two example question-and-SQL reponses.

The question I went over above is a good example of where the zero-shot prompting strategies fell short because it wasn't able to fully understand the question that is was given when I gave it a more complex question. Both of the prompting strategies fell short if I did not give them the full team names if I said 49ers neither strategy was smart enough to know that it needed to look for the San Fransisco 49ers not just the 49ers so in my example questions you will see that both failed those types of questions. They were all failing the questions earlier because I was asking the questions like "Which Quarterback ...?" and it was using that in the database instead of the looking for QB so I gave the prompts more information on that becuase I felt like that was my fault because I placed abreviations instead of full names in the database.

## All other example questions
[View the examples](results.txt)