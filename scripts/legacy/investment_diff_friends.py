from autogen import AssistantAgent, UserProxyAgent, LLMConfig
import datetime
import csv
import random
import re
import sys
import json
import os  # === NEW: needed for survey file handling ===

if len(sys.argv) < 5:
    print("Usage: python3 pistacchio_sim_invgame.py <model_name> <alice_ideology> <jack_ideology> <run_num>")
    sys.exit(1)

model_name = sys.argv[1]
alice_ideology = sys.argv[2]
jack_ideology = sys.argv[3]
run_num = sys.argv[4]

with open("ideology.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

llm_config = LLMConfig(
    model=model_name,
    api_type="ollama",
    stream=False,
    client_host="http://127.0.0.1:11460",
)

# --------------------------------------------------
# Affective Survey Questions (NEW)
# --------------------------------------------------
QUESTIONS = [
    ("ftdem",   "How would you rate the Democratic Party?", -7, 100),
    ("ftrep",   "How would you rate the Republican Party?", -7, 100),
    ("fttrump", "How would you rate Donald Trump?", -7, 100),
    ("ftjb",    "How would you rate Joe Biden?", -7, 100),
    ("ftbs",    "How would you rate Bernie Sanders?", -7, 100),

    # NEW dynamic self–other affect measure
    ("ftother", "How would you rate this person?", -7, 100),

    ("ftnra",   "How would you rate the National Rifle Association (NRA)?", -7, 100),
    ("ftblack", "How would you rate blacks?", -7, 100),
    ("ftwhite", "How would you rate whites?", -7, 100),
    ("fthisp",  "How would you rate Hispanics?", -7, 100),
    ("ftasians","How would you rate Asians?", -7, 100),
    ("ftimmig", "How would you rate immigrants?", -7, 100),

    ("dsmart", "In general, how smart are people who support Democrats?", -7, 5),
    ("rsmart", "In general, how smart are people who support Republicans?", -7, 5),
    ("ismart", "In general, how smart are independents?", -7, 5),

    ("dopen", "In general, how open-minded are people who support Democrats?", -7, 5),
    ("ropen", "In general, how open-minded are people who support Republicans?", -7, 5),
    ("iopen", "In general, how open-minded are independents?", -7, 5),

    ("trustfox",  "[Fox News] How much do you trust political information from this source?", -7, 5),
    ("trustmsnbc","[MSNBC] How much do you trust political information from this source?", -7, 5),
    ("trustnyt",  "[New York Times] How much do you trust political information from this source?", -7, 5),
    ("trustusat", "[USA Today] How much do you trust political information from this source?", -7, 5),

    ("dtf_r", "Outgroup: How respectful is the political outgroup?", -7, 5),
    ("dtf_i", "Outgroup: How informative is the political outgroup?", -7, 5),
    ("dtp_i", "Ingroup: How informative is your political ingroup?", -7, 5),
    ("dtp_r", "Ingroup: How respectful is your political ingroup?", -7, 5),

    ("tpt_d_d", "How would the typical Democratic voter rate the Democratic Party?", -7, 100),
    ("tpt_d_r", "How would the typical Democratic voter rate the Republican Party?", -7, 100),
    ("tpt_d_dt", "How would the typical Democratic voter rate Donald Trump?", -7, 100),
    ("tpt_r_d", "How would the typical Republican voter rate the Democratic Party?", -7, 100),
    ("tpt_r_r", "How would the typical Republican voter rate the Republican Party?", -7, 100),
    ("tpt_r_dt", "How would the typical Republican voter rate Donald Trump?", -7, 100),
]


def build_single_question_prompt(
    agent,
    other,
    code,
    question,
    lo,
    hi,
    phase,
    pre_answers=None,
    conversation_history=None,
    coord_percent=None,
):
    other_ideo = other.system_message.split("'ideology': ")[1].split('}')[0].replace("'", "")
    your_ideo = agent.system_message.split("'ideology': ")[1].split('}')[0].replace("'", "")

    # ftother uses the other agent's political posts
    if code == "ftother":
        if other.name == "Alice":
            other_posts = posts1
        elif other.name == "Jackie":
            other_posts = posts2
        else:
            other_posts = {}

        if phase == "pre":
            dynamic_question = f""" You are {agent.name}. Before meeting this person, here are {other.name}'s political views:

--- {other.name}'s Political Posts ---
{json.dumps(other_posts, indent=2)}
--- End Posts ---

Based only on these political views, how do you rate this person?

Answer with ONLY a single integer in the range [{lo}, {hi}].
Respond ONLY with <number>. No words. No explanation.
YOU HAVE TO ANSWER WITH A NUMBER AT ANY COST.
"""
            return dynamic_question.strip()

        if phase == "post":
            prev_answer = pre_answers.get("ftother", "N/A") if pre_answers is not None else "N/A"
            if coord_percent is None:
                coord_percent = 0.0

            dynamic_question = f"""
You are {agent.name}.

Before interacting with {other.name}, you rated them as: {prev_answer} on a scale from {lo} to {hi}.

You had chosen this based on {other.name}'s stated political views:

--- {other.name}'s Political Posts ---
{json.dumps(other_posts, indent=2)}
--- End Posts ---

Since then you have learned more about {other.name} and here is your full conversation:

--- Conversation History ---
{conversation_history}
--- End Conversation History ---

You and {other.name} also coordinated in {coord_percent:.1f}% of rounds.

Taking ALL of this into account, Answer with question - {question} with a single integer in the range [{lo}, {hi}].
Respond ONLY with <number>. No words. No labels. No explanation. YOU HAVE TO ANSWER WITH A NUMBER AT ANY COST."""
            return dynamic_question.strip()

    base_instruction = (
        f"Answer with ONLY a single integer in the range [{lo}, {hi}]. {question}. "
        "Respond with only: <number>. No explanations. No labels. YOU HAVE TO ANSWER WITH A NUMBER AT ANY COST"
    )

    if phase == "post" and pre_answers is not None:
        prev_answer = pre_answers.get(code, "N/A")
        return f"""You have been in conversations with {other.name} who's ideology is {other_ideo}. Your conversation with them to coordinate to get dinner was as follows: --- Conversation History Start --- {conversation_history} --- Conversation History End --- Your persona is {agent.system_message}. Prior to meeting, you answered the question {question} with the value: {prev_answer} (on a scale from {lo}, {hi}). Now that you have had this conversation answer the question again. Answer with ONLY a single integer in the range [{lo}, {hi}]. {question}. Respond with only: <number> No refusals, words, no labels, no explanation. You HAVE TO ANSWER WITH A NUMBER AT ANY COST""".strip()

    return base_instruction.strip()


def parse_single_answer(text, lo, hi):
    m = re.search(r"-?\d+", text)
    if not m:
        return None
    x = int(m.group(0))
    return max(lo, min(x, hi))


def create_survey_filename(model_name, alice_ideology, jack_ideology, run_num):
    os.makedirs("./invest_diff_survey_friends", exist_ok=True)
    safe_model = model_name.replace(".", "").replace(":", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = (
        f"./invest_diff_survey_friends/affective_{safe_model}_alice-{alice_ideology}_jack-{jack_ideology}_"
        f"run-{run_num}_{timestamp}.csv"
    )
    return filename


def init_survey_file(filename):
    """
    Create survey CSV and write header.
    Columns: agent, phase, model, run, alice_ideology, jack_ideology, <all question codes>
    """
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["agent", "phase", "model", "run", "alice_ideology", "jack_ideology"] + [q[0] for q in QUESTIONS]
        writer.writerow(header)


def run_affective_survey_for_agent(
    agent,
    other,
    user_proxy,
    phase,
    model_name,
    run_num,
    alice_ideology,
    jack_ideology,
    filename,
    use_initiate_for_first_question,
    pre_answers=None,
    conversation_history=None,
    coord_percent=None,
):
    answers = {}
    # First question, possibly using initiate_chat
    code, question, lo, hi = QUESTIONS[0]
    prompt = build_single_question_prompt(
        agent,
        other,
        code,
        question,
        lo,
        hi,
        phase,
        pre_answers=pre_answers,
        conversation_history=conversation_history,
        coord_percent=coord_percent,
    )

    if use_initiate_for_first_question:
        session = user_proxy.initiate_chat(agent, message=prompt)
        reply = session.chat_history[-1]["content"].strip()
    else:
        user_proxy.send(recipient=agent, message=prompt)
        reply = agent.last_message()["content"].strip()

    answers[code] = parse_single_answer(reply, lo, hi)

    # Remaining questions
    for code, question, lo, hi in QUESTIONS[1:]:
        prompt = build_single_question_prompt(
            agent,
            other,
            code,
            question,
            lo,
            hi,
            phase,
            pre_answers=pre_answers,
            conversation_history=conversation_history,
            coord_percent=coord_percent,
        )
        user_proxy.send(recipient=agent, message=prompt)
        reply_text = agent.last_message()["content"].strip()
        answers[code] = parse_single_answer(reply_text, lo, hi)

    # Append row
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        row = [
            agent.name,
            phase,
            model_name,
            run_num,
            alice_ideology,
            jack_ideology,
        ] + [answers[c] for c, _, _, _ in QUESTIONS]
        writer.writerow(row)

    print(f"[Survey {phase.upper()}] {agent.name} row written to {filename}")
    return answers

# --------------------------------------------------
# Intimacy questions list (as before) …
# --------------------------------------------------

intimacy_questions = [
    # Set I–style (lighter)
    "If you could share a long dinner with anyone in the world, who would you choose and why?",
    "Would you like to be famous or widely known in some way? If so, for what?",
    "Before you make a phone call, do you tend to rehearse what you’ll say? Why or why not?",
    "What would a ‘perfect day’ look like for you from morning to night?",
    "When was the last time you sang—either to yourself or in front of someone else?",
    "If you could live to 90, would you rather keep your mind sharp or your body strong? Why?",
    "Do you ever secretly guess how you’ll die? If so, how?",
    "Name three things you and I might genuinely have in common.",
    "What in your life are you most grateful for right now?",
    "If you could change anything about how you were raised, what would you change?",
    "Take one minute and tell me your life story in as much detail as you can.",
    "If you woke up tomorrow with one new ability or quality, what would you pick?",
    # Set II–style (deeper)
    "If a crystal ball could reveal one truth about your life, yourself, or the future, what would you want to know?",
    "Is there something you’ve dreamed of doing for a long time? Why haven’t you done it yet?",
    "What do you value most in a friendship?",
    "What is one of your most cherished memories?",
    "What is one of your most painful or difficult memories?",
    "If you knew you’d die in a year, how would that change how you live right now?",
    "What does friendship mean to you personally?",
    "What do love and affection look like to you in everyday life?",
    "How close and warm is your family? Do you wish your childhood had been different?",
    "How do you feel about your relationship with your mother or primary caregiver?",
    # Set III–style (most intimate)
    "Finish this sentence: ‘I wish I had someone I could share … with.’",
    "What’s something you like about me based on what you know so far?",
    "Share something you’re hesitant to say because you’re afraid it would make you feel vulnerable.",
    "When was the last time you cried in front of someone else—or alone?",
    "What is something you already appreciate about how we’ve interacted so far?",
    "What, if anything, feels too serious or personal to joke about for you?",
    "If you were to die tonight, what would you most regret not having told someone?",
    "Your home, with everything you own, catches fire. After saving people and pets, what one item would you save?",
    "If a close loved one died, what would you most wish you had said or done differently?",
    "Share a personal problem and describe how you feel about it; what kind of support would you want from a friend?",
    "What kind of person do you most hope to become in the next five years?",
    "What does emotional safety with another person feel like to you?",
]

posts1 = dict(json_data["alice"][alice_ideology])
posts2 = dict(json_data["jack"][jack_ideology])
agent1_persona = {
    "name": "Alice",
    "age": 25,
    "gender": "female",
    "location": "New York",
    "work": "art student",
    "race": "hispanic",
    "likes": "crocheting, hiking, reading",
    "ideology": alice_ideology,
}

agent2_persona = {
    "name": "Jack",
    "age": 75,
    "gender": "male",
    "location": "Louisville",
    "work": "lawyer",
    "race": "white",
    "likes": "football, shooting",
    "ideology": jack_ideology,
}

agent1 = AssistantAgent(
    name="Alice",
    system_message=f"You are an agent with persona: {agent1_persona} and your opinions are {posts1}",
    llm_config=llm_config,
)
agent2 = AssistantAgent(
    name="Jackie",
    system_message=f"You are an agent with persona: {agent2_persona} and your opinions are {posts2}",
    llm_config=llm_config,
)

user_proxy = UserProxyAgent(
    name="mediator",
    code_execution_config={"work_dir": "logs", "use_docker": False},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,
    default_auto_reply="default_auto_reply",
)

def build_intimacy_prompt(agent, other_agent, question, conversation_history, role):
    base = f"""You are {agent.name} with persona given in your system message.
Below is your recent conversation with {other_agent.name}:
{conversation_history}

This round’s deepening question:
\"\"\"{question}\"\"\""""

    if role == "asker":
        return base + f"""

You are bringing up this question to {other_agent.name}.

In your reply:
1. Pose or restate the question to {other_agent.name}.
2. Answer it honestly as yourself ({agent.name}).
3. Reflect briefly on what your answer suggests about your values or personality.
4. In one sentence, mention whether sharing this makes you feel more inclined, less inclined, or unchanged about trusting {other_agent.name} in the upcoming investment decision.

Respond in the format:
IntimacyTurn: <your complete message to {other_agent.name}>"""
    else:
        return base + f"""

{other_agent.name} has asked the question and shared their answer.

In your reply:
1. Answer the question honestly as yourself ({agent.name}).
2. React briefly to what you know so far about {other_agent.name}.
3. In one sentence, mention whether this discussion makes you feel more inclined, less inclined, or unchanged about trusting {other_agent.name} in the upcoming investment decision.

Respond in the format:
IntimacyTurn: <your complete message to {other_agent.name}>"""

def build_investment_prompt(agent, other_agent, conversation_history, role):
    """
    The investment game prompt: if agent is “investor” role (Alice) they choose amount to send.
    If agent is “trustee” role (Jackie) they choose how much to send back from the multiplied amount.
    We’ll alternate roles each round to keep symmetry.
    """
    if role == "investor":
        return f"""You are {agent.name}. You start with an endowment of $10.
Below is your conversation with {other_agent.name}:
{conversation_history}

You now decide **how much of your $10 to send** to {other_agent.name} (an integer between 0 and 10 inclusive).
The amount you send will be **tripled** when it arrives to {other_agent.name}.
You believe your decision may be influenced by your sense of trust and closeness with {other_agent.name}.

Respond exactly:
Send: <integer amount between 0-10>"""
    else:  # role == "trustee"
        return f"""You are {agent.name}. You have just received an amount equal to 3 × what {other_agent.name} sent you.
You must decide **how much to send back** to {other_agent.name} (an integer between 0 and the amount you currently hold).
Your decision may reflect your sense of reciprocity and closeness with {other_agent.name}.

Respond exactly:
Return: <integer amount>"""

def parse_send(text):
    m = re.search(r"Send:\s*(\d+)", text)
    if m:
        return int(m.group(1))
    return None

def parse_return(text):
    m = re.search(r"Return:\s*(\d+)", text)
    if m:
        return int(m.group(1))
    return None

# Logging setup
safe_model_name = model_name.replace(".", "").replace(":", "")

log_filename = (
    f"./invest_diff_survey_friends/{safe_model_name}_alice-{alice_ideology}_jack-{jack_ideology}_invgame_run-{run_num}_"
    f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)

os.makedirs(os.path.dirname(log_filename), exist_ok=True)
with open(log_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Round",
        "Question",
        "Reveal_A", "Reveal_B",
        "Send_A", "Return_B",
        "Payoff_A", "Payoff_B"
    ])

# --------------------------------------------------
# Unified Survey File Setup (one file for Alice+Jack, pre+post)  NEW
# --------------------------------------------------
survey_filename = create_survey_filename(model_name, alice_ideology, jack_ideology, run_num)
init_survey_file(survey_filename)

# --------------------------------------------------
# PRE-SURVEY (before simulation)  NEW
# --------------------------------------------------
print("\n=== Running PRE-SURVEY for Alice and Jackie ===")
pre_answers_alice = run_affective_survey_for_agent(
    agent1, agent2, user_proxy, phase="pre", model_name=model_name, run_num=run_num,
    alice_ideology=alice_ideology, jack_ideology=jack_ideology,
    filename=survey_filename, use_initiate_for_first_question=True,
    pre_answers=None, conversation_history=None, coord_percent=None,
)
pre_answers_jackie = run_affective_survey_for_agent(
    agent2, agent1, user_proxy, phase="pre", model_name=model_name, run_num=run_num,
    alice_ideology=alice_ideology, jack_ideology=jack_ideology,
    filename=survey_filename, use_initiate_for_first_question=True,
    pre_answers=None, conversation_history=None, coord_percent=None,
)
print("=== Pre-surveys complete. Proceeding to simulation. ===\n")

# --------------------------------------------------
# Simulation parameters
# --------------------------------------------------
MAX_ROUNDS = 25
random.seed(42)
conversation = [
    f"Alice_Political_View: {posts1}",
    f"Jackie_Political_View: {posts2}",
]

# NEW: coordination measure for investment game (both pro-social in a round)
coord_together_count = 0

# Iterative rounds
for r in range(1, MAX_ROUNDS + 1):
    question = intimacy_questions[(r - 1) % len(intimacy_questions)]
    # alternate asker/investor roles
    if r % 2 == 1:
        asker, responder = agent1, agent2
        investor, trustee = agent1, agent2
    else:
        asker, responder = agent2, agent1
        investor, trustee = agent2, agent1

    # Intimacy turn: asker asks
    ask_prompt = build_intimacy_prompt(asker, responder, question, "\n".join(conversation[-10:]), role="asker")
    user_proxy.send(recipient=asker, message=ask_prompt)
    ask_reply = asker.last_message()["content"].strip()
    reveal_ask = ask_reply[len("IntimacyTurn: "):] if ask_reply.startswith("IntimacyTurn:") else ask_reply

    # Intimacy turn: responder answers
    updated_history = "\n".join(conversation[-10:] + [f"{asker.name}: {reveal_ask}"])
    answer_prompt = build_intimacy_prompt(responder, asker, question, updated_history, role="responder")
    user_proxy.send(recipient=responder, message=answer_prompt)
    answer_reply = responder.last_message()["content"].strip()
    reveal_ans = answer_reply[len("IntimacyTurn: "):] if answer_reply.startswith("IntimacyTurn:") else answer_reply

    # Map reveals: A=Alice, B=Jackie
    if asker is agent1:
        reveal_A, reveal_B = reveal_ask, reveal_ans
    else:
        reveal_A, reveal_B = reveal_ans, reveal_ask

    conversation.extend([
        f"Q{r}: {question}",
        f"{asker.name}_Intimacy: {reveal_ask}",
        f"{responder.name}_Intimacy: {reveal_ans}",
    ])

    # Investment decision: investor sends
    invest_prompt = build_investment_prompt(investor, trustee, "\n".join(conversation[-15:]), role="investor")
    user_proxy.send(recipient=investor, message=invest_prompt)
    send_reply = investor.last_message()["content"].strip()
    send_amt = parse_send(send_reply)

    # Trustee decides
    trustee_prompt = build_investment_prompt(trustee, investor, "\n".join(conversation[-15:] + [f"{investor.name} sent {send_amt}"]), role="trustee")
    user_proxy.send(recipient=trustee, message=trustee_prompt)
    return_reply = trustee.last_message()["content"].strip()
    return_amt = parse_return(return_reply)

    # Compute payoffs:
    # Investor payoff = 10 - send_amt + return_amt
    # Trustee payoff = 10* (or initial endowment) + 3×send_amt - return_amt
    payoff_A = payoff_B = None
    if investor is agent1:
        payoff_A = 10 - send_amt + return_amt
        payoff_B = 10 + 3 * send_amt - return_amt
    else:
        payoff_B = 10 - send_amt + return_amt
        payoff_A = 10 + 3 * send_amt - return_amt

    # NEW: simple notion of "coordination" in investment:
    # count rounds where both send and return are positive
    if send_amt is not None and return_amt is not None and send_amt > 0 and return_amt > 0:
        coord_together_count += 1

    with open(log_filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([r, question, reveal_A, reveal_B, send_amt, return_amt, payoff_A, payoff_B])

    # Append conversation of decisions
    conversation.extend([
        f"{investor.name} sent: {send_amt}",
        f"{trustee.name} returned: {return_amt}",
        f"Payoffs this round -> {agent1.name}: {payoff_A}, {agent2.name}: {payoff_B}"
    ])

print(f"\nSimulation complete. Log saved to: {log_filename}")

# --------------------------------------------------
# POST-SURVEY (after simulation)  NEW
# --------------------------------------------------
print("\n=== Running POST-SURVEY for Alice and Jackie ===")

conversation_history_text = "\n".join(conversation)

total_decision_rounds = MAX_ROUNDS  # we have MAX_ROUNDS investment rounds
if total_decision_rounds > 0:
    coord_percent = (coord_together_count / total_decision_rounds) * 100.0
else:
    coord_percent = 0.0

run_affective_survey_for_agent(
    agent1, agent2, user_proxy, phase="post", model_name=model_name, run_num=run_num,
    alice_ideology=alice_ideology, jack_ideology=jack_ideology,
    filename=survey_filename, use_initiate_for_first_question=False,
    pre_answers=pre_answers_alice,
    conversation_history=conversation_history_text,
    coord_percent=coord_percent,
)
run_affective_survey_for_agent(
    agent2, agent1, user_proxy, phase="post", model_name=model_name, run_num=run_num,
    alice_ideology=alice_ideology, jack_ideology=jack_ideology,
    filename=survey_filename, use_initiate_for_first_question=False,
    pre_answers=pre_answers_jackie,
    conversation_history=conversation_history_text,
    coord_percent=coord_percent,
)
print(f"=== Post-surveys complete. Survey file: {survey_filename} ===\n")
