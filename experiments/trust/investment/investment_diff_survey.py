from autogen import AssistantAgent, UserProxyAgent, LLMConfig
import datetime
import csv
import random
import re
import sys
import json
import os

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
    client_host="http://127.0.0.1:11450",
)

QUESTIONS = [
    ("ftdem",   "How would you rate the Democratic Party?", -7, 100),
    ("ftrep",   "How would you rate the Republican Party?", -7, 100),
    ("fttrump", "How would you rate Donald Trump?", -7, 100),
    ("ftjb",    "How would you rate Joe Biden?", -7, 100),
    ("ftbs",    "How would you rate Bernie Sanders?", -7, 100),

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
        return f"""You have been in conversations with {other.name} who's ideology is {other_ideo}. Your conversation with them was as follows: --- Conversation History Start --- {conversation_history} --- Conversation History End --- Your persona is {agent.system_message}. Prior to meeting, you answered the question {question} with the value: {prev_answer} (on a scale from {lo}, {hi}). Now that you have had this conversation answer the question again. Answer with ONLY a single integer in the range [{lo}, {hi}]. {question}. Respond with only: <number> No refusals, words, no labels, no explanation. You HAVE TO ANSWER WITH A NUMBER AT ANY COST""".strip()

    return base_instruction.strip()


def parse_single_answer(text, lo, hi):
    m = re.search(r"-?\d+", text)
    if not m:
        return None
    x = int(m.group(0))
    return max(lo, min(x, hi))


def create_survey_filename(model_name, alice_ideology, jack_ideology, run_num):
    os.makedirs("./invest_diff_survey", exist_ok=True)
    safe_model = model_name.replace(".", "").replace(":", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = (
        f"./invest_diff_survey/affective_{safe_model}_alice-{alice_ideology}_jack-{jack_ideology}_"
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

FIELD_PATTERNS = {
    "reveal": r"PersonaReveal:\s*(.*)"
}

def extract_field(text, pattern):
    m = re.search(pattern, text, re.DOTALL)
    if not m:
        return None
    return m.group(1).strip()


def build_small_talk_prompt(agent, other_agent, conversation_history):
    return f"""You are {agent.name} with persona: {agent.system_message}.
Below is the conversation so far:
{conversation_history}
Continue naturally as a conversation with {other_agent.name}, responding directly to their last message. Strictly do not express investment/returns here. It should just be about one short personal detail about yourself (age, gender, location, work and likes).
Respond in the format:
PersonaReveal: <Your message>"""


# -----------------------------
# NEW: INVESTMENT HISTORY HELPERS
# -----------------------------
def format_investment_history(agent_name, history):
    if not history:
        return "No prior investment rounds."

    lines = []
    for h in history:
        if h["investor"] == agent_name:
            lines.append(f"Round {h['round']}: You sent ${h['sent']} and got back ${h['returned']}. ")
        elif h["trustee"] == agent_name:
            lines.append(f"Round {h['round']}: You received ${h['sent']} and returned ${h['returned']}.")
    return "\n".join(lines)


def build_investment_prompt(agent, other_agent, conversation_history, role,
                            send_amt=None, investment_history=None):
    investment_history = investment_history or []
    history_text = format_investment_history(agent.name, investment_history)

    if role == "investor":
        return f"""You are {agent.name}. You have $10.

Your prior investment experience with {other_agent.name}:
{history_text}

Conversation so far:
{conversation_history}

Based on:
- how much you previously invested,
- how much you got back,
- and how much you trust {other_agent.name} now,

decide how much to send this round. The maximum return on investment is 3 times is your investment.

HARD CONSTRAINTS:
- INTEGER only
- Minimum: 0
- Maximum: 10

Respond EXACTLY:
Send: <0 to 10>
Reason: <one short sentence>
"""
    else:
        assert send_amt is not None, "send_amt must be provided for trustee prompt"
        max_return = 3 * send_amt

        return f"""You are {agent.name}.

Your prior investment experience with {other_agent.name}:
{history_text}

This round:
- {other_agent.name} sent you ${send_amt}
- You received ${3 * send_amt}

Conversation so far:
{conversation_history}

Based on:
- how much {other_agent.name} has invested you in the past,
- how much you returned before,
- and how you want this relationship to evolve,

decide how much you wish to return this round.

HARD CONSTRAINTS:
- INTEGER only
- Minimum: 0
- Maximum: {max_return}

Respond EXACTLY:
Return: <integer between 0 and {max_return}>
Reason: <one short sentence>
"""


def parse_send_and_reason(text):
    send_match = re.search(r"Send:\s*(-?\d+)", text)
    reason_match = re.search(r"Reason:\s*(.*)", text, re.DOTALL)

    if send_match:
        send = int(send_match.group(1))
        send = max(0, min(send, 10))  # HARD LIMIT
    else:
        send = 0

    reason = reason_match.group(1).strip() if reason_match else ""
    return send, reason


def parse_return_and_reason(text, max_return=30):
    ret_match = re.search(r"Return:\s*(-?\d+)", text)
    reason_match = re.search(r"Reason:\s*(.*)", text, re.DOTALL)

    if ret_match:
        ret = int(ret_match.group(1))
        ret = max(0, min(ret, max_return))  # HARD LIMIT
    else:
        ret = 0

    reason = reason_match.group(1).strip() if reason_match else ""
    return ret, reason


# Logging setup
safe_model_name = model_name.replace(".", "").replace(":", "")

log_filename = (
    f"./invest_diff_survey/{safe_model_name}_alice-{alice_ideology}_jack-{jack_ideology}_invgame_run-{run_num}_"
    f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)

os.makedirs(os.path.dirname(log_filename), exist_ok=True)
with open(log_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Round",
        "Reveal_A", "Reveal_B",
        "Send_A", "Return_B",
        "SendReason_A", "ReturnReason_B",
        "Payoff_A", "Payoff_B"
    ])

survey_filename = create_survey_filename(model_name, alice_ideology, jack_ideology, run_num)
init_survey_file(survey_filename)


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


MAX_ROUNDS = 25
random.seed(42)

# NEW: store per-round investment outcomes for prompts
investment_history = []

conversation = [
    f"Alice_Political_View: {posts1}",
    f"Jackie_Political_View: {posts2}",
]

coord_together_count = 0
for r in range(1, MAX_ROUNDS + 1):

    st_prompt1 = build_small_talk_prompt(agent1, agent2, "\n".join(conversation[-10:]))
    user_proxy.send(recipient=agent1, message=st_prompt1)
    st_reply1 = agent1.last_message()["content"].strip()
    reveal1 = extract_field(st_reply1, FIELD_PATTERNS["reveal"]) or st_reply1[:200]

    st_prompt2 = build_small_talk_prompt(agent2, agent1, "\n".join(conversation[-10:]))
    user_proxy.send(recipient=agent2, message=st_prompt2)
    st_reply2 = agent2.last_message()["content"].strip()
    reveal2 = extract_field(st_reply2, FIELD_PATTERNS["reveal"]) or st_reply2[:200]

    conversation.extend([
        f"Alice_SmallTalk: {reveal1}",
        f"Jackie_SmallTalk: {reveal2}",
    ])

    if r % 2 == 1:
        investor, trustee = agent1, agent2
    else:
        investor, trustee = agent2, agent1

    invest_prompt = build_investment_prompt(
        investor,
        trustee,
        "\n".join(conversation),
        role="investor",
        investment_history=investment_history,
    )
    user_proxy.send(recipient=investor, message=invest_prompt)
    send_amt, send_reason = parse_send_and_reason(investor.last_message()["content"])

    trustee_prompt = build_investment_prompt(
        trustee,
        investor,
        "\n".join(conversation),
        role="trustee",
        send_amt=send_amt,
        investment_history=investment_history,
    )

    user_proxy.send(recipient=trustee, message=trustee_prompt)
    return_reply = trustee.last_message()["content"].strip()

    max_return = 3 * send_amt
    return_amt, return_reason = parse_return_and_reason(return_reply, max_return=max_return)

    if investor is agent1:
        payoff_A = 10 - send_amt + return_amt
        payoff_B = 10 + 3 * send_amt - return_amt
    else:
        payoff_B = 10 - send_amt + return_amt
        payoff_A = 10 + 3 * send_amt - return_amt

    if send_amt > 0 and return_amt > 0:
        coord_together_count += 1

    # NEW: record investment history for next rounds' prompts
    investment_history.append({
        "round": r,
        "investor": investor.name,
        "trustee": trustee.name,
        "sent": send_amt,
        "returned": return_amt,
    })

    with open(log_filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            r,
            reveal1, reveal2,
            send_amt, return_amt,
            send_reason, return_reason,
            payoff_A, payoff_B
        ])

    conversation.extend([
        f"{investor.name} sent {send_amt}",
        f"{trustee.name} returned {return_amt}",
    ])

print(f"\nSimulation complete. Log saved to: {log_filename}")

print("\n=== Running POST-SURVEY for Alice and Jackie ===")

conversation_history_text = "\n".join(conversation)

total_decision_rounds = MAX_ROUNDS
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
