import hikari
import lightbulb
import asyncio
import os

token = os.getenv('DISCORD_TOKEN')

# Global flags to control game state
end = False
start = False

# List of supported categories
SUPPORTED_CATEGORIES = ['general', 'science', 'history', 'movies']

# Dictionary of trivia questions categorized by topic
TRIVIA_QUESTIONS = {
    'general': [
        {'question': 'What is the capital of France?', 'answer': 'Paris'},
        {'question': 'Who wrote "Romeo and Juliet"?', 'answer': 'William Shakespeare'},
        {'question': 'What is the tallest mammal in the world?', 'answer': 'Giraffe'},
        {'question': 'In which year did the Titanic sink?', 'answer': '1912'},
        {'question': 'What is the largest ocean on Earth?', 'answer': 'Pacific Ocean'},
        {'question': 'What is the currency of Japan?', 'answer': 'Japanese Yen'},
        {'question': 'Who painted the famous painting "The Starry Night"?', 'answer': 'Vincent van Gogh'},
        {'question': 'What is the national animal of Australia?', 'answer': 'Kangaroo'},
        {'question': 'Who is known as the father of modern physics?', 'answer': 'Albert Einstein'},
        {'question': 'What is the chemical symbol for gold?', 'answer': 'Au'},
    ],
    'science': [
        {'question': 'Who proposed the theory of evolution by natural selection?', 'answer': 'Charles Darwin'},
        {'question': 'What is the unit of measurement for electrical resistance?', 'answer': 'Ohm'},
        {'question': 'What is the largest planet in our solar system?', 'answer': 'Jupiter'},
        {'question': 'Who discovered penicillin?', 'answer': 'Alexander Fleming'},
        {'question': 'What is the atomic number of carbon?', 'answer': '6'},
        {'question': 'What type of blood is known as the universal donor?', 'answer': 'O-negative'},
        {'question': 'What is the process by which plants make their food called?', 'answer': 'Photosynthesis'},
        {'question': 'What is the study of the Earth and its features called?', 'answer': 'Geology'},
        {'question': 'Who is known as the father of modern chemistry?', 'answer': 'Antoine Lavoisier'},
        {'question': 'What is the chemical formula for table salt?', 'answer': 'NaCl'},
    ],
    'history': [
        {'question': 'Who was the first emperor of Rome?', 'answer': 'Augustus Caesar'},
        {'question': 'Which war is known as the Great War?', 'answer': 'World War I'},
        {'question': 'Who was the first woman to fly solo across the Atlantic Ocean?', 'answer': 'Amelia Earhart'},
        {'question': 'What year did the Berlin Wall fall?', 'answer': '1989'},
        {'question': 'Who was the first European explorer to reach India by sea?', 'answer': 'Vasco da Gama'},
        {'question': 'What was the ancient name of Istanbul?', 'answer': 'Constantinople'},
        {'question': 'Which ancient wonder of the world was located in Egypt?', 'answer': 'The Great Pyramid of Giza'},
        {'question': 'What year did Christopher Columbus first reach the Americas?', 'answer': '1492'},
        {'question': 'Who was the first female Prime Minister of the United Kingdom?', 'answer': 'Margaret Thatcher'},
        {'question': 'Who was the longest-reigning British monarch?', 'answer': 'Queen Victoria'},
    ],
    'movies': [
        {'question': 'Who played Jack Dawson in the movie "Titanic"?', 'answer': 'Leonardo DiCaprio'},
        {'question': 'What is the highest-grossing animated film of all time?', 'answer': 'Frozen II'},
        {'question': 'Who directed the movie "Inception"?', 'answer': 'Christopher Nolan'},
        {'question': 'Which film won the Academy Award for Best Picture in 2020?', 'answer': 'Parasite'},
        {'question': 'In the movie "The Godfather", who played the character Michael Corleone?', 'answer': 'Al Pacino'},
        {'question': 'What is the name of the ship in the movie "Pirates of the Caribbean"?', 'answer': 'The Black Pearl'},
        {'question': 'Who played Hermione Granger in the "Harry Potter" film series?', 'answer': 'Emma Watson'},
        {'question': 'Which movie features the character Hannibal Lecter?', 'answer': 'The Silence of the Lambs'},
        {'question': 'Who directed the movie "The Dark Knight"?', 'answer': 'Christopher Nolan'},
        {'question': 'In the movie "Forrest Gump", who played the title character?', 'answer': 'Tom Hanks'},
    ],
}


# Function to validate the category
def validate_category(category):
    return category.lower() in SUPPORTED_CATEGORIES

# Function to fetch trivia questions by category
def fetch_questions_by_category(category):
    return [question['question'] for question in TRIVIA_QUESTIONS[category.lower()]]

# Function to check the answer
def check_answer(category,ans_num,user_ans):
    return TRIVIA_QUESTIONS[category.lower()][ans_num]['answer'].lower() == user_ans.lower()

# Create a Discord bot instance
bot = lightbulb.BotApp(token=token, intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT,default_enabled_guilds=(1241396034077327513))

# Command to start the trivia game
@bot.command
@lightbulb.option('category','Choose a category for the trivia game. Available categories: general, science, history, movies.')
@lightbulb.command('start_trivia','Start the trivia game!')
@lightbulb.implements(lightbulb.SlashCommand)

async def start_trivia(ctx):
    global end
    end = False
    global start
    start = True
    if validate_category(ctx.options.category):
        await ctx.respond(f"```fix\nStarting a trivia game with the '{ctx.options.category}' category!\nYou have 15 seconds to answer each question```\n")
        questions = fetch_questions_by_category(ctx.options.category)
        score = 0
        for i, question in enumerate(questions, start=1):
            if end:
                break;
            await ctx.respond(f"```fix\nQuestion {i}: {question}\n```")
            try:
                event = await bot.wait_for(hikari.MessageCreateEvent, timeout=15.0)
                user_answer = event.message.content.strip()
                if check_answer(ctx.options.category, i-1, user_answer) and not end:
                    score += 1
                    await ctx.respond("```diff\n+ Correct!\n```")
                elif not end:
                    await ctx.respond(f"```diff\n- Sorry, the correct answer was: {TRIVIA_QUESTIONS[ctx.options.category.lower()][i-1]['answer']}\n```")
            except asyncio.TimeoutError:
                if len(questions) > i:
                    await ctx.respond("```diff\n- No response within the time limit. Moving to the next question.\n```")
                else:
                    await ctx.respond("```diff\n- No response within the time limit.\n```")
        if not end:
            await ctx.respond(f"Trivia game ended! Your score: {score}/{len(questions)}")
    else:
        await ctx.respond(f"Sorry, '{ctx.options.category}' is not a valid category. Please choose from: {', '.join(SUPPORTED_CATEGORIES)}")

# Command to end the trivia game
@bot.command
@lightbulb.command('end_trivia', 'End the trivia game!')
@lightbulb.implements(lightbulb.SlashCommand)
async def end_game(ctx):
    global end
    end = True
    if start:
        await ctx.respond("Trivia game ended!")
    else:
        await ctx.respond("You are not currently playing any trivia game.")

# Run the bot
if __name__ == '__main__':
    bot.run()
