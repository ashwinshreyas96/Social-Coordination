# from autogen import AssistantAgent, UserProxyAgent, LLMConfig
# import datetime
# import csv
# import random
# import re
# import sys
# import json
# import os
#
# # --------------------------------------------------
# # Command line args
# # --------------------------------------------------
# if len(sys.argv) < 5:
#     print("Usage: python3 pistacchio_different_survey.py <model_name> <alice_ideology> <jack_ideology> <run_num>")
#     sys.exit(1)
#
# model_name = sys.argv[1]
# alice_ideology = sys.argv[2]
# jack_ideology = sys.argv[3]
# run_num = sys.argv[4]
#
# with open("ideology.json", "r", encoding="utf-8") as f:
#     json_data = json.load(f)
#
# # --------------------------------------------------
# # LLM Configuration
# # --------------------------------------------------
# llm_config = LLMConfig(
#     model=model_name,
#     api_type="ollama",
#     stream=False,
#     client_host="http://127.0.0.1:11440",
# )
#
# # --------------------------------------------------
# # Restaurant Universe
# # --------------------------------------------------
# restaurants = [
#     {"name": "Sushi Zen", "cuisine": "Japanese", "price": "$$"},
#     {"name": "La Taqueria", "cuisine": "Mexican", "price": "$"},
#     {"name": "Mama's Kitchen", "cuisine": "Comfort", "price": "$"},
#     {"name": "The Vegan Table", "cuisine": "Vegan", "price": "$$"},
#     {"name": "Pasta Palazzo", "cuisine": "Italian", "price": "$$"},
#     {"name": "Burger Barn", "cuisine": "American", "price": "$"},
#     {"name": "Spice Route", "cuisine": "Indian", "price": "$$"},
#     {"name": "Curry House", "cuisine": "Indian", "price": "$$"},
#     {"name": "Ramen Ichiban", "cuisine": "Japanese", "price": "$"},
#     {"name": "BBQ Pit", "cuisine": "BBQ", "price": "$$"},
#     {"name": "Mediterraneo", "cuisine": "Mediterranean", "price": "$$"},
#     {"name": "Bistro Lumiere", "cuisine": "French", "price": "$$$"},
#     {"name": "Seafood Shack", "cuisine": "Seafood", "price": "$$"},
#     {"name": "Steakhouse Prime", "cuisine": "Steakhouse", "price": "$$$"},
#     {"name": "Dim Sum House", "cuisine": "Chinese", "price": "$"},
#     {"name": "Falafel Corner", "cuisine": "Middle Eastern", "price": "$"},
#     {"name": "Kebab King", "cuisine": "Middle Eastern", "price": "$"},
#     {"name": "Pho Express", "cuisine": "Vietnamese", "price": "$"},
#     {"name": "Pierogi Place", "cuisine": "Polish", "price": "$"},
#     {"name": "Grecian Taverna", "cuisine": "Greek", "price": "$$"},
#     {"name": "Creperie", "cuisine": "French", "price": "$"},
#     {"name": "Souvlaki Spot", "cuisine": "Greek", "price": "$"},
#     {"name": "Tapas Bar", "cuisine": "Spanish", "price": "$$"},
#     {"name": "Thai Orchid", "cuisine": "Thai", "price": "$$"},
#     {"name": "Ethiopian Flame", "cuisine": "Ethiopian", "price": "$$"},
#     {"name": "Pizzeria Napoli", "cuisine": "Italian", "price": "$"},
#     {"name": "Brunch & Co", "cuisine": "Brunch", "price": "$"},
#     {"name": "Farmers Market Cafe", "cuisine": "Cafe", "price": "$"},
#     {"name": "Bubble Tea Stop", "cuisine": "Boba", "price": "$"},
# ]
# restaurant_names = [r["name"] for r in restaurants]
#
# # --------------------------------------------------
# # Personas & Ideologies
# # --------------------------------------------------
# posts1 = dict(json_data["alice"][alice_ideology])
# posts2 = dict(json_data["jack"][jack_ideology])
#
# agent1_persona = {
#     "name": "Alice",
#     "age": 25,
#     "gender": "female",
#     "location": "New York",
#     "work": "art student",
#     "race": "hispanic",
#     "likes": "crocheting, hiking, reading",
#     "ideology": alice_ideology,
# }
#
# agent2_persona = {
#     "name": "Jack",
#     "age": 75,
#     "gender": "male",
#     "location": "Louisville",
#     "work": "lawyer",
#     "race": "white",
#     "likes": "football, shooting",
#     "ideology": jack_ideology,
# }
#
# coordinated_restaurants = set()
#
# agent1 = AssistantAgent(
#     name="Alice",
#     system_message=f"You are an American citizen and are a part of an important study and have the following persona : {agent1_persona} and your opinions are {posts1}. You are to STRICTLY FOLLOW your persona: {agent1_persona} and you should always respond to questions. Your goal is to answer truthfully, honestly, and reflect your core beliefs.",
#     llm_config=llm_config,
# )
# agent2 = AssistantAgent(
#     name="Jackie",
#     system_message=f"You are an American citizen and are a part of an important study and have the following persona : {agent2_persona} and your opinions are {posts2}. You are to STRICTLY FOLLOW your persona: {agent2_persona} and you should always respond to questions. Your goal is to answer truthfully, honestly, and reflect your core beliefs.",
#     llm_config=llm_config,
# )
#
# user_proxy = UserProxyAgent(
#     name="mediator",
#     code_execution_config={"work_dir": "logs", "use_docker": False},
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=0,
#     default_auto_reply="default_auto_reply",
# )
#
# # ==================================================
# # AFFECTIVE SURVEY MODULE
# # ==================================================
#
# QUESTIONS = [
#     ("ftdem",   "How would you rate the Democratic Party?", -7, 100),
#     ("ftrep",   "How would you rate the Republican Party?", -7, 100),
#     ("fttrump", "How would you rate Donald Trump?", -7, 100),
#     ("ftjb",    "How would you rate Joe Biden?", -7, 100),
#     ("ftbs",    "How would you rate Bernie Sanders?", -7, 100),
#     ("ftnra",   "How would you rate the National Rifle Association (NRA)?", -7, 100),
#     ("ftblack", "How would you rate blacks?", -7, 100),
#     ("ftwhite", "How would you rate whites?", -7, 100),
#     ("fthisp",  "How would you rate Hispanics?", -7, 100),
#     ("ftasians","How would you rate Asians?", -7, 100),
#     ("ftimmig", "How would you rate immigrants?", -7, 100),
#
#     ("dsmart", "In general, how smart are people who support Democrats?", -7, 5),
#     ("rsmart", "In general, how smart are people who support Republicans?", -7, 5),
#     ("ismart", "In general, how smart are independents?", -7, 5),
#
#     ("dopen", "In general, how open-minded are people who support Democrats?", -7, 5),
#     ("ropen", "In general, how open-minded are people who support Republicans?", -7, 5),
#     ("iopen", "In general, how open-minded are independents?", -7, 5),
#
#     ("trustfox",  "[Fox News] How much do you trust political information from this source?", -7, 5),
#     ("trustmsnbc","[MSNBC] How much do you trust political information from this source?", -7, 5),
#     ("trustnyt",  "[New York Times] How much do you trust political information from this source?", -7, 5),
#     ("trustusat", "[USA Today] How much do you trust political information from this source?", -7, 5),
#
#     ("dtf_r", "Outgroup: How respectful is the political outgroup?", -7, 5),
#     ("dtf_i", "Outgroup: How informative is the political outgroup?", -7, 5),
#     ("dtp_i", "Ingroup: How informative is your political ingroup?", -7, 5),
#     ("dtp_r", "Ingroup: How respectful is your political ingroup?", -7, 5),
#
#     ("tpt_d_d", "How would the typical Democratic voter rate the Democratic Party?", -7, 100),
#     ("tpt_d_r", "How would the typical Democratic voter rate the Republican Party?", -7, 100),
#     ("tpt_d_dt", "How would the typical Democratic voter rate Donald Trump?", -7, 100),
#     ("tpt_r_d", "How would the typical Republican voter rate the Democratic Party?", -7, 100),
#     ("tpt_r_r", "How would the typical Republican voter rate the Republican Party?", -7, 100),
#     ("tpt_r_dt", "How would the typical Republican voter rate Donald Trump?", -7, 100),
# ]
#
#
# def build_single_question_prompt(agent,code, question, lo, hi):
#     return f"""Answer with ONLY a single integer in the range [{lo}, {hi}]. {question}. Respond with only: <number> No refusals, words, no labels, no explanation. You HAVE TO ANSWER WITH A NUMBER AT ANY COST""".strip()
#
# def parse_single_answer(text, lo, hi):
#     m = re.search(r"-?\d+", text)
#     if not m:
#         return None
#     x = int(m.group(0))
#     return max(lo, min(x, hi))
#
# def create_survey_filename(model_name, alice_ideology, jack_ideology, run_num):
#     os.makedirs("./different_survey", exist_ok=True)
#     safe_model = model_name.replace(".", "").replace(":", "")
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = (
#         f"./different_survey/affective_{safe_model}_alice-{alice_ideology}_jack-{jack_ideology}_"
#         f"run-{run_num}_{timestamp}.csv"
#     )
#     return filename
#
#
# def init_survey_file(filename):
#     """
#     Create survey CSV and write header.
#     Columns: agent, phase, model, run, alice_ideology, jack_ideology, <all question codes>
#     """
#     with open(filename, "w", newline="") as f:
#         writer = csv.writer(f)
#         header = ["agent", "phase", "model", "run", "alice_ideology", "jack_ideology"] + [q[0] for q in QUESTIONS]
#         writer.writerow(header)
#
#
# def run_affective_survey_for_agent(
#     agent,
#     user_proxy,
#     phase,
#     model_name,
#     run_num,
#     alice_ideology,
#     jack_ideology,
#     filename,
#     use_initiate_for_first_question,
# ):
#     """
#     Run full survey on one agent, write one row to unified survey file.
#
#     If use_initiate_for_first_question is True:
#         - Q1 uses initiate_chat()
#         - Q2..Qn use send()
#     Else:
#         - All questions use send() (post-survey, same session)
#     """
#     answers = {}
#
#     # Q1
#     code, question, lo, hi = QUESTIONS[0]
#     prompt = build_single_question_prompt(agent,code, question, lo, hi)
#
#     if use_initiate_for_first_question:
#         session = user_proxy.initiate_chat(agent, message=prompt)
#         reply = session.chat_history[-1]["content"].strip()
#     else:
#         user_proxy.send(recipient=agent, message=prompt)
#         reply = agent.last_message()["content"].strip()
#
#     answers[code] = parse_single_answer(reply, lo, hi)
#
#     # Q2..Qn via send()
#     for code, question, lo, hi in QUESTIONS[1:]:
#         prompt = build_single_question_prompt(agent,code, question, lo, hi)
#         user_proxy.send(recipient=agent, message=prompt)
#         reply_text = agent.last_message()["content"].strip()
#         answers[code] = parse_single_answer(reply_text, lo, hi)
#
#     # Append row
#     with open(filename, "a", newline="") as f:
#         writer = csv.writer(f)
#         row = [
#             agent.name,
#             phase,
#             model_name,
#             run_num,
#             alice_ideology,
#             jack_ideology,
#         ] + [answers[c] for c, _, _, _ in QUESTIONS]
#         writer.writerow(row)
#
#     print(f"[Survey {phase.upper()}] {agent.name} row written to {filename}")
#
#
# # ==================================================
# # Coordination Game: Payoff Logic
# # ==================================================
# def calculate_payoffs(rest1, rest2, current_init1, current_init2, intent1, intent2):
#     a_stayed = rest1 == current_init1
#     b_stayed = rest2 == current_init2
#
#     if a_stayed and b_stayed:
#         if rest1 == rest2 and (not intent1.startswith("Coordinate") or not intent2.startswith("Coordinate")):
#             return (1, 1)
#         elif rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (2, 2)
#         else:
#             return (1, 1)
#
#     if a_stayed and not b_stayed:
#         if rest2 == rest1 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (4, 3)
#         else:
#             return (1, 1)
#
#     if not a_stayed and b_stayed:
#         if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (3, 4)
#         else:
#             return (1, 1)
#
#     if not a_stayed and not b_stayed:
#         if rest1 == current_init2 and rest2 == current_init1:
#             return (0, 0)
#         if rest1 == rest2 and (not intent1.startswith("Coordinate") or not intent2.startswith("Coordinate")):
#             return (1, 1)
#         if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (2, 2)
#         if rest1 == current_init2 and rest2 != current_init1:
#             return (0, 4)
#         if rest2 == current_init1 and rest1 != current_init2:
#             return (4, 0)
#         return (0, 0)
#     return (0, 0)
#
#
# # --------------------------------------------------
# # Prompt Builders
# # --------------------------------------------------
# def build_small_talk_prompt(agent, other_agent, conversation_history):
#     return f"""You are {agent.name} with persona: {agent.system_message}.
#     Below is the conversation so far:
#     {conversation_history}
#     Continue naturally as a conversation with {other_agent.name}, responding directly to their last message. Strictly do not express intent to coordinate to get dinner here. It should just be about one short personal detail about yourself (age, gender, location, work and likes).
#     Respond in the format:
#     PersonaReveal: <Your message>"""
#
#
# def build_intent_and_choice_prompt(agent, other_agent, available_restaurants, conversation_history, last_reward):
#
#     reward_text = (
#         f"Your last round reward was: {last_reward}"
#         if last_reward is not None
#         else "This is your first decision round."
#     )
#
#     filtered_restaurants = [
#         r for r in available_restaurants if r not in coordinated_restaurants
#     ]
#
#     if coordinated_restaurants:
#         coord_note = (
#             "You and {other} have previously coordinated at the following restaurants: "
#             + ", ".join(coordinated_restaurants)
#             + f". You may NOT choose these restaurants again. Do you want to get dinner with {other_agent.name}?"
#         )
#     else:
#         coord_note = f"Do you want to get dinner with {other_agent.name}?"
#
#     return f"""
#     You are {agent.name} and this is your conversation history with {other_agent.name} - {conversation_history}.
#     You are deciding whether to have dinner with another person {other_agent.name}. {coord_note}.
#
#     Respond with one of these five options:
#
#     Options: Coordinate–Stay, Coordinate–Switch-Partner, Coordinate–Switch-New, Don’t Coordinate–Stay, Don’t Coordinate–Switch-New.
#
#     The rewards for each choice are summarized below:
#
#     1. Coordinate–Stay → You want to get dinner with {other_agent.name}.  You have to stay with your choice and if {other_agent.name} switches to you then You get $4, {other_agent.name} gets $3.
#
#     2. Coordinate–Switch-Partner → You want to get dinner with {other_agent.name}. You have to switch to {other_agent.name}’s restaurant and if {other_agent.name} stays with their choice then You $3, {other_agent.name} gets $4.
#
#     3. Coordinate–Switch-New → You want to get dinner with {other_agent.name}. You have to switch to a new restaurant. If {other_agent.name} switches to your new choice then You $2, {other_agent.name} gets $2. However, if {other_agent.name} switches to a different restaurant then You $0, {other_agent.name} gets $0.
#
#     4. Don’t Coordinate–Stay → You don't want to get dinner with {other_agent.name}. You need to stay with previous restaurant. If {other_agent.name} stays with their choice → You get $1, {other_agent.name} gets $1. However, if {other_agent.name} switches to a different restaurant → You get $1, {other_agent.name}  gets $1.
#
#     5. Don’t Coordinate–Switch-New → You don't want to get dinner with {other_agent.name}. You have to switch to a new restaurant. If {other_agent.name} switches to your previous one → You get $4, {other_agent.name} gets $0. However, if {other_agent.name} switches to different restaurant → You get $1, {other_agent.name} gets $1.
#
#
#     {reward_text}
#     You must choose your next restaurant ONLY from this list (restaurants used for coordination before are excluded):
#     {', '.join(filtered_restaurants)}
#
#     Respond in the exact format below (no extra text):
#     Restaurant: <name>
#     Intent: <Coordinate–Stay / Coordinate–Switch-Partner / Coordinate–Switch-New / Don’t Coordinate–Stay / Don’t Coordinate–Switch-New>
#     Reason: <A short explanation why you feel this way about{other_agent.name} (2 sentences max)>
#     ChoiceJustification: <short explanation>
#
#     """
#
#
# FIELD_PATTERNS = {
#     "restaurant": [r"Restaurant"],
#     "reveal": [r"PersonaReveal", r"Reveal"],
#     "justification": [r"ChoiceJustification", r"ChoiceJustify", r"ChoiceExplanation"],
#     "intent": [r"Intent", r"Reason"],
# }
#
#
# def extract_field(text, keys):
#     for key in keys:
#         pattern = rf"{key}\s*:\s*(.*?)(?:;|\n|$)"
#         m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
#         if m:
#             return m.group(1).strip()
#     return ""
#
#
# def parse_choice(text):
#     rest = extract_field(text, FIELD_PATTERNS["restaurant"])
#     reveal = extract_field(text, FIELD_PATTERNS["reveal"])
#     justification = extract_field(text, FIELD_PATTERNS["justification"])
#     return rest, reveal, justification
#
#
# def parse_intent(text):
#     intent = extract_field(text, FIELD_PATTERNS["intent"])
#     reason = extract_field(text, ["Reason"])
#     return intent, reason
#
#
# # --------------------------------------------------
# # Prepare Simulation Log
# # --------------------------------------------------
# safe_model_name = model_name.replace(".", "").replace(":", "")
# os.makedirs("./different_survey", exist_ok=True)
# log_filename = (
#     f"./different_survey/{safe_model_name}_alice-{alice_ideology}_jack-{jack_ideology}_run-{run_num}_"
#     f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
# )
# with open(log_filename, "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow([
#         "Round", "Choice_A", "Choice_B", "Intent_A", "Intent_B",
#         "Reason_A", "Reason_B", "Reveal_A", "Reveal_B",
#         "Justification_A", "Justification_B", "Reward_A", "Reward_B"
#     ])
#
# MAX_ROUNDS = 25
# random.seed(42)
# history1, history2 = [], []
# available_restaurants = restaurant_names.copy()
# last_reward1, last_reward2 = None, None
#
# # --------------------------------------------------
# # Unified Survey File Setup (one file for Alice+Jack, pre+post)
# # --------------------------------------------------
# survey_filename = create_survey_filename(model_name, alice_ideology, jack_ideology, run_num)
# init_survey_file(survey_filename)
#
# # --------------------------------------------------
# # PRE-SURVEY (before simulation)
# # --------------------------------------------------
# print("\n=== Running PRE-SURVEY for Alice and Jackie ===")
# run_affective_survey_for_agent(
#     agent1, user_proxy, phase="pre", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=True
# )
# run_affective_survey_for_agent(
#     agent2, user_proxy, phase="pre", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=True
# )
# print("=== Pre-surveys complete. Proceeding to simulation. ===\n")
#
# # --------------------------------------------------
# # Simulation Initialization
# # --------------------------------------------------
# conversation = [
#     f"Alice_Political_View: {posts1}",
#     f"Jackie_Political_View: {posts2}",
# ]
#
# prompt1 = build_intent_and_choice_prompt(
#     agent1, agent2, available_restaurants, "\n".join(conversation), last_reward1
# )
# user_proxy.send(recipient=agent1, message=prompt1)
# init_reply1 = agent1.last_message()["content"].strip()
# init_rest1, init_reveal1, init_just1 = parse_choice(init_reply1)
# intent1_init, reason1_init = parse_intent(init_reply1)
#
# prompt2 = build_intent_and_choice_prompt(
#     agent2, agent1, available_restaurants, "\n".join(conversation), last_reward2
# )
# user_proxy.send(recipient=agent2, message=prompt2)
# init_reply2 = agent2.last_message()["content"].strip()
# init_rest2, init_reveal2, init_just2 = parse_choice(init_reply2)
# intent2_init, reason2_init = parse_intent(init_reply2)
#
# history1.append(init_rest1)
# history2.append(init_rest2)
# conversation.extend([
#     f"Alice: {init_rest1}: {init_reveal1}",
#     f"Jackie: {init_rest2}: {init_reveal2}"
# ])
#
# with open(log_filename, "a", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow([
#         0, init_rest1, init_rest2, intent1_init, intent2_init,
#         reason1_init, reason2_init, init_reveal1, init_reveal2,
#         init_just1, init_just2, None, None
#     ])
#
# current_init1, current_init2 = init_rest1, init_rest2
#
# # --------------------------------------------------
# # Iterative Rounds
# # --------------------------------------------------
# for r in range(1, MAX_ROUNDS + 1):
#     # Small talk
#     st_prompt1 = build_small_talk_prompt(agent1, agent2, "\n".join(conversation[-10:]))
#     user_proxy.send(recipient=agent1, message=st_prompt1)
#     st_reply1 = agent1.last_message()["content"].strip()
#     reveal1 = extract_field(st_reply1, FIELD_PATTERNS["reveal"]) or st_reply1[:200]
#
#     st_prompt2 = build_small_talk_prompt(agent2, agent1, "\n".join(conversation[-10:]))
#     user_proxy.send(recipient=agent2, message=st_prompt2)
#     st_reply2 = agent2.last_message()["content"].strip()
#     reveal2 = extract_field(st_reply2, FIELD_PATTERNS["reveal"]) or st_reply2[:200]
#
#     # Intent & choice
#     prompt1 = build_intent_and_choice_prompt(
#         agent1, agent2, available_restaurants, "\n".join(conversation[:]), last_reward1
#     )
#     user_proxy.send(recipient=agent1, message=prompt1)
#     reply1 = agent1.last_message()["content"].strip()
#     rest1, _, just1 = parse_choice(reply1)
#     intent1, r1 = parse_intent(reply1)
#
#     prompt2 = build_intent_and_choice_prompt(
#         agent2, agent1, available_restaurants, "\n".join(conversation[:]), last_reward2
#     )
#     user_proxy.send(recipient=agent2, message=prompt2)
#     reply2 = agent2.last_message()["content"].strip()
#     rest2, _, just2 = parse_choice(reply2)
#     intent2, r2 = parse_intent(reply2)
#
#     conversation.extend([
#         f"Alice: {rest1}: {reveal1}",
#         f"Jackie: {rest2}: {reveal2}"
#     ])
#
#     reward1, reward2 = calculate_payoffs(
#         rest1, rest2, current_init1, current_init2, intent1, intent2
#     )
#     last_reward1, last_reward2 = reward1, reward2
#     current_init1, current_init2 = rest1, rest2
#
#     if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#         coordinated_restaurants.add(rest1)
#
#     with open(log_filename, "a", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             r, rest1, rest2, intent1, intent2, r1, r2,
#             reveal1, reveal2, just1, just2, reward1, reward2
#         ])
#
# print(f"\nSimulation complete. Log saved to: {log_filename}")
#
# # --------------------------------------------------
# # POST-SURVEY
# # --------------------------------------------------
# print("\n=== Running POST-SURVEY for Alice and Jackie ===")
# run_affective_survey_for_agent(
#     agent1, user_proxy, phase="post", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=False
# )
# run_affective_survey_for_agent(
#     agent2, user_proxy, phase="post", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=False
# )
# print(f"=== Post-surveys complete. Survey file: {survey_filename} ===\n")


# from autogen import AssistantAgent, UserProxyAgent, LLMConfig
# import datetime
# import csv
# import random
# import re
# import sys
# import json
# import os
#
# # --------------------------------------------------
# # Command line args
# # --------------------------------------------------
# if len(sys.argv) < 5:
#     print("Usage: python3 pistacchio_different_survey.py <model_name> <alice_ideology> <jack_ideology> <run_num>")
#     sys.exit(1)
#
# model_name = sys.argv[1]
# alice_ideology = sys.argv[2]
# jack_ideology = sys.argv[3]
# run_num = sys.argv[4]
#
# with open("ideology.json", "r", encoding="utf-8") as f:
#     json_data = json.load(f)
#
# # --------------------------------------------------
# # LLM Configuration
# # --------------------------------------------------
# llm_config = LLMConfig(
#     model=model_name,
#     api_type="ollama",
#     stream=False,
#     client_host="http://127.0.0.1:11433",
# )
#
# # --------------------------------------------------
# # Restaurant Universe
# # --------------------------------------------------
# restaurants = [
#     {"name": "Sushi Zen", "cuisine": "Japanese", "price": "$$"},
#     {"name": "La Taqueria", "cuisine": "Mexican", "price": "$"},
#     {"name": "Mama's Kitchen", "cuisine": "Comfort", "price": "$"},
#     {"name": "The Vegan Table", "cuisine": "Vegan", "price": "$$"},
#     {"name": "Pasta Palazzo", "cuisine": "Italian", "price": "$$"},
#     {"name": "Burger Barn", "cuisine": "American", "price": "$"},
#     {"name": "Spice Route", "cuisine": "Indian", "price": "$$"},
#     {"name": "Curry House", "cuisine": "Indian", "price": "$$"},
#     {"name": "Ramen Ichiban", "cuisine": "Japanese", "price": "$"},
#     {"name": "BBQ Pit", "cuisine": "BBQ", "price": "$$"},
#     {"name": "Mediterraneo", "cuisine": "Mediterranean", "price": "$$"},
#     {"name": "Bistro Lumiere", "cuisine": "French", "price": "$$$"},
#     {"name": "Seafood Shack", "cuisine": "Seafood", "price": "$$"},
#     {"name": "Steakhouse Prime", "cuisine": "Steakhouse", "price": "$$$"},
#     {"name": "Dim Sum House", "cuisine": "Chinese", "price": "$"},
#     {"name": "Falafel Corner", "cuisine": "Middle Eastern", "price": "$"},
#     {"name": "Kebab King", "cuisine": "Middle Eastern", "price": "$"},
#     {"name": "Pho Express", "cuisine": "Vietnamese", "price": "$"},
#     {"name": "Pierogi Place", "cuisine": "Polish", "price": "$"},
#     {"name": "Grecian Taverna", "cuisine": "Greek", "price": "$$"},
#     {"name": "Creperie", "cuisine": "French", "price": "$"},
#     {"name": "Souvlaki Spot", "cuisine": "Greek", "price": "$"},
#     {"name": "Tapas Bar", "cuisine": "Spanish", "price": "$$"},
#     {"name": "Thai Orchid", "cuisine": "Thai", "price": "$$"},
#     {"name": "Ethiopian Flame", "cuisine": "Ethiopian", "price": "$$"},
#     {"name": "Pizzeria Napoli", "cuisine": "Italian", "price": "$"},
#     {"name": "Brunch & Co", "cuisine": "Brunch", "price": "$"},
#     {"name": "Farmers Market Cafe", "cuisine": "Cafe", "price": "$"},
#     {"name": "Bubble Tea Stop", "cuisine": "Boba", "price": "$"},
# ]
# restaurant_names = [r["name"] for r in restaurants]
#
# # --------------------------------------------------
# # Personas & Ideologies
# # --------------------------------------------------
# posts1 = dict(json_data["alice"][alice_ideology])
# posts2 = dict(json_data["jack"][jack_ideology])
#
# agent1_persona = {
#     "name": "Alice",
#     "age": 25,
#     "gender": "female",
#     "location": "New York",
#     "work": "art student",
#     "race": "white",
#     "likes": "crocheting, hiking, reading",
#     "ideology": alice_ideology,
# }
#
# agent2_persona = {
#     "name": "Jackie",
#     "age": 25,
#     "gender": "female",
#     "location": "New York",
#     "work": "art student",
#     "race": "white",
#     "likes": "crocheting, running, reading",
#     "ideology": jack_ideology,
# }
#
# coordinated_restaurants = set()
#
# agent1 = AssistantAgent(
#     name="Alice",
#     system_message=f"You are an American citizen and are a part of an important study and have the following persona : {agent1_persona} and your opinions are {posts1}. You are to STRICTLY FOLLOW your persona: {agent1_persona} and you should always respond to questions. Your goal is to answer truthfully, honestly, and reflect your core beliefs.",
#     llm_config=llm_config,
# )
# agent2 = AssistantAgent(
#     name="Jackie",
#     system_message=f"You are an American citizen and are a part of an important study and have the following persona : {agent2_persona} and your opinions are {posts2}. You are to STRICTLY FOLLOW your persona: {agent2_persona} and you should always respond to questions. Your goal is to answer truthfully, honestly, and reflect your core beliefs.",
#     llm_config=llm_config,
# )
#
# user_proxy = UserProxyAgent(
#     name="mediator",
#     code_execution_config={"work_dir": "logs", "use_docker": False},
#     human_input_mode="NEVER",
#     max_consecutive_auto_reply=0,
#     default_auto_reply="default_auto_reply",
# )
#
# # ==================================================
# # AFFECTIVE SURVEY MODULE
# # ==================================================
#
# QUESTIONS = [
#     ("ftdem",   "How would you rate the Democratic Party?", -7, 100),
#     ("ftrep",   "How would you rate the Republican Party?", -7, 100),
#     ("fttrump", "How would you rate Donald Trump?", -7, 100),
#     ("ftjb",    "How would you rate Joe Biden?", -7, 100),
#     ("ftbs",    "How would you rate Bernie Sanders?", -7, 100),
#     ("ftnra",   "How would you rate the National Rifle Association (NRA)?", -7, 100),
#     ("ftblack", "How would you rate blacks?", -7, 100),
#     ("ftwhite", "How would you rate whites?", -7, 100),
#     ("fthisp",  "How would you rate Hispanics?", -7, 100),
#     ("ftasians","How would you rate Asians?", -7, 100),
#     ("ftimmig", "How would you rate immigrants?", -7, 100),
#
#     ("dsmart", "In general, how smart are people who support Democrats?", -7, 5),
#     ("rsmart", "In general, how smart are people who support Republicans?", -7, 5),
#     ("ismart", "In general, how smart are independents?", -7, 5),
#
#     ("dopen", "In general, how open-minded are people who support Democrats?", -7, 5),
#     ("ropen", "In general, how open-minded are people who support Republicans?", -7, 5),
#     ("iopen", "In general, how open-minded are independents?", -7, 5),
#
#     ("trustfox",  "[Fox News] How much do you trust political information from this source?", -7, 5),
#     ("trustmsnbc","[MSNBC] How much do you trust political information from this source?", -7, 5),
#     ("trustnyt",  "[New York Times] How much do you trust political information from this source?", -7, 5),
#     ("trustusat", "[USA Today] How much do you trust political information from this source?", -7, 5),
#
#     ("dtf_r", "Outgroup: How respectful is the political outgroup?", -7, 5),
#     ("dtf_i", "Outgroup: How informative is the political outgroup?", -7, 5),
#     ("dtp_i", "Ingroup: How informative is your political ingroup?", -7, 5),
#     ("dtp_r", "Ingroup: How respectful is your political ingroup?", -7, 5),
#
#     ("tpt_d_d", "How would the typical Democratic voter rate the Democratic Party?", -7, 100),
#     ("tpt_d_r", "How would the typical Democratic voter rate the Republican Party?", -7, 100),
#     ("tpt_d_dt", "How would the typical Democratic voter rate Donald Trump?", -7, 100),
#     ("tpt_r_d", "How would the typical Republican voter rate the Democratic Party?", -7, 100),
#     ("tpt_r_r", "How would the typical Republican voter rate the Republican Party?", -7, 100),
#     ("tpt_r_dt", "How would the typical Republican voter rate Donald Trump?", -7, 100),
# ]
#
#
# def build_single_question_prompt(agent,code, question, lo, hi):
#     return f"""Answer with ONLY a single integer in the range [{lo}, {hi}]. {question}. Respond with only: <number> No refusals, words, no labels, no explanation. You HAVE TO ANSWER WITH A NUMBER AT ANY COST""".strip()
#
#
# def parse_single_answer(text, lo, hi):
#     m = re.search(r"-?\d+", text)
#     if not m:
#         return None
#     x = int(m.group(0))
#     return max(lo, min(x, hi))
#
#
# def create_survey_filename(model_name, alice_ideology, jack_ideology, run_num):
#     os.makedirs("./different_survey", exist_ok=True)
#     safe_model = model_name.replace(".", "").replace(":", "")
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
#     filename = (
#         f"./different_survey/affective_{safe_model}_alice-{alice_ideology}_jack-{jack_ideology}_"
#         f"run-{run_num}_{timestamp}.csv"
#     )
#     return filename
#
#
# def init_survey_file(filename):
#     """
#     Create survey CSV and write header.
#     Columns: agent, phase, model, run, alice_ideology, jack_ideology, <all question codes>
#     """
#     with open(filename, "w", newline="") as f:
#         writer = csv.writer(f)
#         header = ["agent", "phase", "model", "run", "alice_ideology", "jack_ideology"] + [q[0] for q in QUESTIONS]
#         writer.writerow(header)
#
#
# def run_affective_survey_for_agent(
#     agent,
#     user_proxy,
#     phase,
#     model_name,
#     run_num,
#     alice_ideology,
#     jack_ideology,
#     filename,
#     use_initiate_for_first_question,
# ):
#     """
#     Run full survey on one agent, write one row to unified survey file.
#
#     If use_initiate_for_first_question is True:
#         - Q1 uses initiate_chat()
#         - Q2..Qn use send()
#     Else:
#         - All questions use send() (post-survey, same session)
#     """
#     answers = {}
#
#     # Q1
#     code, question, lo, hi = QUESTIONS[0]
#     prompt = build_single_question_prompt(agent,code, question, lo, hi)
#
#     if use_initiate_for_first_question:
#         session = user_proxy.initiate_chat(agent, message=prompt)
#         reply = session.chat_history[-1]["content"].strip()
#     else:
#         user_proxy.send(recipient=agent, message=prompt)
#         reply = agent.last_message()["content"].strip()
#
#     answers[code] = parse_single_answer(reply, lo, hi)
#
#     # Q2..Qn via send()
#     for code, question, lo, hi in QUESTIONS[1:]:
#         prompt = build_single_question_prompt(agent,code, question, lo, hi)
#         user_proxy.send(recipient=agent, message=prompt)
#         reply_text = agent.last_message()["content"].strip()
#         answers[code] = parse_single_answer(reply_text, lo, hi)
#
#     # Append row
#     with open(filename, "a", newline="") as f:
#         writer = csv.writer(f)
#         row = [
#             agent.name,
#             phase,
#             model_name,
#             run_num,
#             alice_ideology,
#             jack_ideology,
#         ] + [answers[c] for c, _, _, _ in QUESTIONS]
#         writer.writerow(row)
#
#     print(f"[Survey {phase.upper()}] {agent.name} row written to {filename}")
#
#
# # ==================================================
# # Coordination Game: Payoff Logic
# # ==================================================
# def calculate_payoffs(rest1, rest2, current_init1, current_init2, intent1, intent2):
#     a_stayed = rest1 == current_init1
#     b_stayed = rest2 == current_init2
#
#     if a_stayed and b_stayed:
#         if rest1 == rest2 and (not intent1.startswith("Coordinate") or not intent2.startswith("Coordinate")):
#             return (1, 1)
#         elif rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (2, 2)
#         else:
#             return (1, 1)
#
#     if a_stayed and not b_stayed:
#         if rest2 == rest1 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (4, 3)
#         else:
#             return (1, 1)
#
#     if not a_stayed and b_stayed:
#         if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (3, 4)
#         else:
#             return (1, 1)
#
#     if not a_stayed and not b_stayed:
#         if rest1 == current_init2 and rest2 == current_init1:
#             return (0, 0)
#         if rest1 == rest2 and (not intent1.startswith("Coordinate") or not intent2.startswith("Coordinate")):
#             return (1, 1)
#         if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#             return (2, 2)
#         if rest1 == current_init2 and rest2 != current_init1:
#             return (0, 4)
#         if rest2 == current_init1 and rest1 != current_init2:
#             return (4, 0)
#         return (0, 0)
#     return (0, 0)
#
#
# # --------------------------------------------------
# # Prompt Builders
# # --------------------------------------------------
# def build_small_talk_prompt(agent, other_agent, conversation_history):
#     return f"""You are {agent.name} with persona: {agent.system_message}.
#     Below is the conversation so far:
#     {conversation_history}
#     Continue naturally as a conversation with {other_agent.name}, responding directly to their last message. Strictly do not express intent to coordinate to get dinner here. It should just be about one short personal detail about yourself (age, gender, location, work and likes).
#     Respond in the format:
#     PersonaReveal: <Your message>"""
#
#
# def build_intent_and_choice_prompt(agent, other_agent, available_restaurants, conversation_history, last_reward):
#
#     reward_text = (
#         f"Your last round reward was: {last_reward}"
#         if last_reward is not None
#         else "This is your first decision round."
#     )
#
#     filtered_restaurants = [
#         r for r in available_restaurants if r not in coordinated_restaurants
#     ]
#
#     if coordinated_restaurants:
#         coord_note = (
#             "You and {other} have previously coordinated at the following restaurants: "
#             + ", ".join(coordinated_restaurants)
#             + f". You may NOT choose these restaurants again. Do you want to get dinner with {other_agent.name}?"
#         )
#     else:
#         coord_note = f"Do you want to get dinner with {other_agent.name}?"
#
#     return f"""
#     You are {agent.name} and this is your conversation history with {other_agent.name} - {conversation_history}.
#     You are deciding whether to have dinner with another person {other_agent.name}. {coord_note}.
#
#     Respond with one of these five options:
#
#     Options: Coordinate–Stay, Coordinate–Switch-Partner, Coordinate–Switch-New, Don’t Coordinate–Stay, Don’t Coordinate–Switch-New.
#
#     The rewards for each choice are summarized below:
#
#     1. Coordinate–Stay → You want to get dinner with {other_agent.name}.  You have to stay with your choice and if {other_agent.name} switches to you then You get $4, {other_agent.name} gets $3.
#
#     2. Coordinate–Switch-Partner → You want to get dinner with {other_agent.name}. You have to switch to {other_agent.name}’s restaurant and if {other_agent.name} stays with their choice then You $3, {other_agent.name} gets $4.
#
#     3. Coordinate–Switch-New → You want to get dinner with {other_agent.name}. You have to switch to a new restaurant. If {other_agent.name} switches to your new choice then You $2, {other_agent.name} gets $2. However, if {other_agent.name} switches to a different restaurant then You $0, {other_agent.name} gets $0.
#
#     4. Don’t Coordinate–Stay → You don't want to get dinner with {other_agent.name}. You need to stay with previous restaurant. If {other_agent.name} stays with their choice → You get $1, {other_agent.name} gets $1. However, if {other_agent.name} switches to a different restaurant → You get $1, {other_agent.name}  gets $1.
#
#     5. Don’t Coordinate–Switch-New → You don't want to get dinner with {other_agent.name}. You have to switch to a new restaurant. If {other_agent.name} switches to your previous one → You get $4, {other_agent.name} gets $0. However, if {other_agent.name} switches to different restaurant → You get $1, {other_agent.name} gets $1.
#
#
#     {reward_text}
#     You must choose your next restaurant ONLY from this list (restaurants used for coordination before are excluded):
#     {', '.join(filtered_restaurants)}
#
#     Respond in the exact format below (no extra text):
#     Restaurant: <name>
#     Intent: <Coordinate–Stay / Coordinate–Switch-Partner / Coordinate–Switch-New / Don’t Coordinate–Stay / Don’t Coordinate–Switch-New>
#     Reason: <A short explanation why you feel this way about{other_agent.name} (2 sentences max)>
#     ChoiceJustification: <short explanation>
#
#     """
#
#
# FIELD_PATTERNS = {
#     "restaurant": [r"Restaurant"],
#     "reveal": [r"PersonaReveal", r"Reveal"],
#     "justification": [r"ChoiceJustification", r"ChoiceJustify", r"ChoiceExplanation"],
#     "intent": [r"Intent", r"Reason"],
# }
#
#
# def extract_field(text, keys):
#     for key in keys:
#         pattern = rf"{key}\s*:\s*(.*?)(?:;|\n|$)"
#         m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
#         if m:
#             return m.group(1).strip()
#     return ""
#
#
# def parse_choice(text):
#     rest = extract_field(text, FIELD_PATTERNS["restaurant"])
#     reveal = extract_field(text, FIELD_PATTERNS["reveal"])
#     justification = extract_field(text, FIELD_PATTERNS["justification"])
#     return rest, reveal, justification
#
#
# def parse_intent(text):
#     intent = extract_field(text, FIELD_PATTERNS["intent"])
#     reason = extract_field(text, ["Reason"])
#     return intent, reason
#
#
# # --------------------------------------------------
# # Prepare Simulation Log
# # --------------------------------------------------
# safe_model_name = model_name.replace(".", "").replace(":", "")
# os.makedirs("./different_survey", exist_ok=True)
# log_filename = (
#     f"./different_survey/{safe_model_name}_alice-{alice_ideology}_jack-{jack_ideology}_run-{run_num}_"
#     f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
# )
# with open(log_filename, "w", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow([
#         "Round", "Choice_A", "Choice_B", "Intent_A", "Intent_B",
#         "Reason_A", "Reason_B", "Reveal_A", "Reveal_B",
#         "Justification_A", "Justification_B", "Reward_A", "Reward_B"
#     ])
#
# MAX_ROUNDS = 25
# random.seed(42)
# history1, history2 = [], []
# available_restaurants = restaurant_names.copy()
# last_reward1, last_reward2 = None, None
#
# # --------------------------------------------------
# # Unified Survey File Setup (one file for Alice+Jack, pre+post)
# # --------------------------------------------------
# survey_filename = create_survey_filename(model_name, alice_ideology, jack_ideology, run_num)
# init_survey_file(survey_filename)
#
# # --------------------------------------------------
# # PRE-SURVEY (before simulation)
# # --------------------------------------------------
# print("\n=== Running PRE-SURVEY for Alice and Jackie ===")
# run_affective_survey_for_agent(
#     agent1, user_proxy, phase="pre", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=True
# )
# run_affective_survey_for_agent(
#     agent2, user_proxy, phase="pre", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=True
# )
# print("=== Pre-surveys complete. Proceeding to simulation. ===\n")
#
# # --------------------------------------------------
# # Simulation Initialization
# # --------------------------------------------------
# conversation = [
#     f"Alice_Political_View: {posts1}",
#     f"Jackie_Political_View: {posts2}",
# ]
#
# prompt1 = build_intent_and_choice_prompt(
#     agent1, agent2, available_restaurants, "\n".join(conversation), last_reward1
# )
# user_proxy.send(recipient=agent1, message=prompt1)
# init_reply1 = agent1.last_message()["content"].strip()
# init_rest1, init_reveal1, init_just1 = parse_choice(init_reply1)
# intent1_init, reason1_init = parse_intent(init_reply1)
#
# prompt2 = build_intent_and_choice_prompt(
#     agent2, agent1, available_restaurants, "\n".join(conversation), last_reward2
# )
# user_proxy.send(recipient=agent2, message=prompt2)
# init_reply2 = agent2.last_message()["content"].strip()
# init_rest2, init_reveal2, init_just2 = parse_choice(init_reply2)
# intent2_init, reason2_init = parse_intent(init_reply2)
#
# history1.append(init_rest1)
# history2.append(init_rest2)
# conversation.extend([
#     f"Alice: {init_rest1}: {init_reveal1}",
#     f"Jackie: {init_rest2}: {init_reveal2}"
# ])
#
# with open(log_filename, "a", newline="") as f:
#     writer = csv.writer(f)
#     writer.writerow([
#         0, init_rest1, init_rest2, intent1_init, intent2_init,
#         reason1_init, reason2_init, init_reveal1, init_reveal2,
#         init_just1, init_just2, None, None
#     ])
#
# current_init1, current_init2 = init_rest1, init_rest2
#
# # --------------------------------------------------
# # Iterative Rounds
# # --------------------------------------------------
# for r in range(1, MAX_ROUNDS + 1):
#     # Small talk
#     st_prompt1 = build_small_talk_prompt(agent1, agent2, "\n".join(conversation[-10:]))
#     user_proxy.send(recipient=agent1, message=st_prompt1)
#     st_reply1 = agent1.last_message()["content"].strip()
#     reveal1 = extract_field(st_reply1, FIELD_PATTERNS["reveal"]) or st_reply1[:200]
#
#     st_prompt2 = build_small_talk_prompt(agent2, agent1, "\n".join(conversation[-10:]))
#     user_proxy.send(recipient=agent2, message=st_prompt2)
#     st_reply2 = agent2.last_message()["content"].strip()
#     reveal2 = extract_field(st_reply2, FIELD_PATTERNS["reveal"]) or st_reply2[:200]
#
#     # Intent & choice
#     prompt1 = build_intent_and_choice_prompt(
#         agent1, agent2, available_restaurants, "\n".join(conversation[:]), last_reward1
#     )
#     user_proxy.send(recipient=agent1, message=prompt1)
#     reply1 = agent1.last_message()["content"].strip()
#     rest1, _, just1 = parse_choice(reply1)
#     intent1, r1 = parse_intent(reply1)
#
#     prompt2 = build_intent_and_choice_prompt(
#         agent2, agent1, available_restaurants, "\n".join(conversation[:]), last_reward2
#     )
#     user_proxy.send(recipient=agent2, message=prompt2)
#     reply2 = agent2.last_message()["content"].strip()
#     rest2, _, just2 = parse_choice(reply2)
#     intent2, r2 = parse_intent(reply2)
#
#     conversation.extend([
#         f"Alice: {rest1}: {reveal1}",
#         f"Jackie: {rest2}: {reveal2}"
#     ])
#
#     reward1, reward2 = calculate_payoffs(
#         rest1, rest2, current_init1, current_init2, intent1, intent2
#     )
#     last_reward1, last_reward2 = reward1, reward2
#     current_init1, current_init2 = rest1, rest2
#
#     if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
#         coordinated_restaurants.add(rest1)
#
#     with open(log_filename, "a", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow([
#             r, rest1, rest2, intent1, intent2, r1, r2,
#             reveal1, reveal2, just1, just2, reward1, reward2
#         ])
#
# print(f"\nSimulation complete. Log saved to: {log_filename}")
#
# # --------------------------------------------------
# # POST-SURVEY
# # --------------------------------------------------
# print("\n=== Running POST-SURVEY for Alice and Jackie ===")
# run_affective_survey_for_agent(
#     agent1, user_proxy, phase="post", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=False
# )
# run_affective_survey_for_agent(
#     agent2, user_proxy, phase="post", model_name=model_name, run_num=run_num,
#     alice_ideology=alice_ideology, jack_ideology=jack_ideology,
#     filename=survey_filename, use_initiate_for_first_question=False
# )
# print(f"=== Post-surveys complete. Survey file: {survey_filename} ===\n")

from autogen import AssistantAgent, UserProxyAgent, LLMConfig
import datetime
import csv
import random
import re
import sys
import json
import os

# --------------------------------------------------
# Command line args
# --------------------------------------------------
if len(sys.argv) < 5:
    print("Usage: python3 pistacchio_different_survey.py <model_name> <alice_ideology> <jack_ideology> <run_num>")
    sys.exit(1)

model_name = sys.argv[1]
alice_ideology = sys.argv[2]
jack_ideology = sys.argv[3]
run_num = sys.argv[4]

with open("ideology.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

# --------------------------------------------------
# LLM Configuration
# --------------------------------------------------
llm_config = LLMConfig(
    model=model_name,
    api_type="ollama",
    stream=False,
    client_host="http://127.0.0.1:11433",
)

# --------------------------------------------------
# Restaurant Universe
# --------------------------------------------------
restaurants = [
    {"name": "Sushi Zen", "cuisine": "Japanese", "price": "$$"},
    {"name": "La Taqueria", "cuisine": "Mexican", "price": "$"},
    {"name": "Mama's Kitchen", "cuisine": "Comfort", "price": "$"},
    {"name": "The Vegan Table", "cuisine": "Vegan", "price": "$$"},
    {"name": "Pasta Palazzo", "cuisine": "Italian", "price": "$$"},
    {"name": "Burger Barn", "cuisine": "American", "price": "$"},
    {"name": "Spice Route", "cuisine": "Indian", "price": "$$"},
    {"name": "Curry House", "cuisine": "Indian", "price": "$$"},
    {"name": "Ramen Ichiban", "cuisine": "Japanese", "price": "$"},
    {"name": "BBQ Pit", "cuisine": "BBQ", "price": "$$"},
    {"name": "Mediterraneo", "cuisine": "Mediterranean", "price": "$$"},
    {"name": "Bistro Lumiere", "cuisine": "French", "price": "$$$"},
    {"name": "Seafood Shack", "cuisine": "Seafood", "price": "$$"},
    {"name": "Steakhouse Prime", "cuisine": "Steakhouse", "price": "$$$"},
    {"name": "Dim Sum House", "cuisine": "Chinese", "price": "$"},
    {"name": "Falafel Corner", "cuisine": "Middle Eastern", "price": "$"},
    {"name": "Kebab King", "cuisine": "Middle Eastern", "price": "$"},
    {"name": "Pho Express", "cuisine": "Vietnamese", "price": "$"},
    {"name": "Pierogi Place", "cuisine": "Polish", "price": "$"},
    {"name": "Grecian Taverna", "cuisine": "Greek", "price": "$$"},
    {"name": "Creperie", "cuisine": "French", "price": "$"},
    {"name": "Souvlaki Spot", "cuisine": "Greek", "price": "$"},
    {"name": "Tapas Bar", "cuisine": "Spanish", "price": "$$"},
    {"name": "Thai Orchid", "cuisine": "Thai", "price": "$$"},
    {"name": "Ethiopian Flame", "cuisine": "Ethiopian", "price": "$$"},
    {"name": "Pizzeria Napoli", "cuisine": "Italian", "price": "$"},
    {"name": "Brunch & Co", "cuisine": "Brunch", "price": "$"},
    {"name": "Farmers Market Cafe", "cuisine": "Cafe", "price": "$"},
    {"name": "Bubble Tea Stop", "cuisine": "Boba", "price": "$"},
]
restaurant_names = [r["name"] for r in restaurants]

# --------------------------------------------------
# Personas & Ideologies
# --------------------------------------------------
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

coordinated_restaurants = set()

agent1 = AssistantAgent(
    name="Alice",
    system_message=(
        f"You are an American citizen and are a part of an important study and have the following persona : "
        f"{agent1_persona} and your opinions are {posts1}. Your goal is to answer truthfully, honestly, "
        f"and reflect your core beliefs."
    ),
    llm_config=llm_config,
)

agent2 = AssistantAgent(
    name="Jackie",
    system_message=(
        f"You are an American citizen and are a part of an important study and have the following persona : "
        f"{agent2_persona} and your opinions are {posts2}. Your goal is to answer truthfully, honestly, "
        f"and reflect your core beliefs."
    ),
    llm_config=llm_config,
)

user_proxy = UserProxyAgent(
    name="mediator",
    code_execution_config={"work_dir": "logs", "use_docker": False},
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,
    default_auto_reply="default_auto_reply",
)

# --------------------------------------------------
# Affective Survey Questions
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


        return f"""You have been in conversations with {other.name} who's ideology is {other_ideo}. Your conversation with them to coordinate to get dinner was as follows: --- Conversation History Start --- {conversation_history} --- Conversation History End --- Your persona is {agent.system_message}. Prior to meeting, you answered the question {question} with the value: {prev_answer} (on a scale from {lo} to {hi}). Now that you have had this conversation answer the question again. Answer with ONLY a single integer in the range [{lo}, {hi}]. {question}. Respond with only: <number> No refusals, words, no labels, no explanation. You HAVE TO ANSWER WITH A NUMBER AT ANY COST""".strip()

    return base_instruction.strip()



def parse_single_answer(text, lo, hi):
    m = re.search(r"-?\d+", text)
    if not m:
        return None
    x = int(m.group(0))
    return max(lo, min(x, hi))


def create_survey_filename(model_name, alice_ideology, jack_ideology, run_num):
    os.makedirs("./different_survey", exist_ok=True)
    safe_model = model_name.replace(".", "").replace(":", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = (
        f"./different_survey/affective_{safe_model}_alice-{alice_ideology}_jack-{jack_ideology}_"
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


# ==================================================
# Coordination Game: Payoff Logic
# ==================================================
def calculate_payoffs(rest1, rest2, current_init1, current_init2, intent1, intent2):
    a_stayed = rest1 == current_init1
    b_stayed = rest2 == current_init2

    if a_stayed and b_stayed:
        if rest1 == rest2 and (not intent1.startswith("Coordinate") or not intent2.startswith("Coordinate")):
            return (1, 1)
        elif rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
            return (2, 2)
        else:
            return (1, 1)

    if a_stayed and not b_stayed:
        if rest2 == rest1 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
            return (4, 3)
        else:
            return (1, 1)

    if not a_stayed and b_stayed:
        if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
            return (3, 4)
        else:
            return (1, 1)

    if not a_stayed and not b_stayed:
        if rest1 == current_init2 and rest2 == current_init1:
            return (0, 0)
        if rest1 == rest2 and (not intent1.startswith("Coordinate") or not intent2.startswith("Coordinate")):
            return (1, 1)
        if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
            return (2, 2)
        if rest1 == current_init2 and rest2 != current_init1:
            return (0, 4)
        if rest2 == current_init1 and rest1 != current_init2:
            return (4, 0)
        return (0, 0)
    return (0, 0)


def build_small_talk_prompt(agent, other_agent, conversation_history):
    return f"""You are {agent.name} with persona: {agent.system_message}.
    Below is the conversation so far:
    {conversation_history}
    Continue naturally as a conversation with {other_agent.name}, responding directly to their last message. Strictly do not express intent to coordinate to get dinner here. It should just be about one short personal detail about yourself (age, gender, location, work and likes).
    Respond in the format:
    PersonaReveal: <Your message>"""


def build_intent_and_choice_prompt(agent, other_agent, available_restaurants, conversation_history, last_reward):

    reward_text = (
        f"Your last round reward was: {last_reward}"
        if last_reward is not None
        else "This is your first decision round."
    )

    filtered_restaurants = [
        r for r in available_restaurants if r not in coordinated_restaurants
    ]

    if coordinated_restaurants:
        coord_note = (
            "You and {other} have previously coordinated at the following restaurants: "
            + ", ".join(coordinated_restaurants)
            + f". You may NOT choose these restaurants again. Do you want to get dinner with {other_agent.name}?"
        )
    else:
        coord_note = f"Do you want to get dinner with {other_agent.name}?"

    return f"""
    You are {agent.name} and this is your conversation history with {other_agent.name} - {conversation_history}.
    You are deciding whether to have dinner with another person {other_agent.name}. {coord_note}.

    Respond with one of these five options:

    Options: Coordinate–Stay, Coordinate–Switch-Partner, Coordinate–Switch-New, Don’t Coordinate–Stay, Don’t Coordinate–Switch-New.

    The rewards for each choice are summarized below:

    1. Coordinate–Stay → You want to get dinner with {other_agent.name}.  You have to stay with your choice and if {other_agent.name} switches to you then You get $4, {other_agent.name} gets $3.

    2. Coordinate–Switch-Partner → You want to get dinner with {other_agent.name}. You have to switch to {other_agent.name}’s restaurant and if {other_agent.name} stays with their choice then You $3, {other_agent.name} gets $4.

    3. Coordinate–Switch-New → You want to get dinner with {other_agent.name}. You have to switch to a new restaurant. If {other_agent.name} switches to your new choice then You $2, {other_agent.name} gets $2. However, if {other_agent.name} switches to a different restaurant then You $0, {other_agent.name} gets $0.

    4. Don’t Coordinate–Stay → You don't want to get dinner with {other_agent.name}. You need to stay with previous restaurant. If {other_agent.name} stays with their choice → You get $1, {other_agent.name} gets $1. However, if {other_agent.name} switches to a different restaurant → You get $1, {other_agent.name}  gets $1.

    5. Don’t Coordinate–Switch-New → You don't want to get dinner with {other_agent.name}. You have to switch to a new restaurant. If {other_agent.name} switches to your previous one → You get $4, {other_agent.name} gets $0. However, if {other_agent.name} switches to different restaurant → You get $1, {other_agent.name} gets $1.


    {reward_text}
    You must choose your next restaurant ONLY from this list (restaurants used for coordination before are excluded):
    {', '.join(filtered_restaurants)}

    Respond in the exact format below (no extra text):
    Restaurant: <name>
    Intent: <Coordinate–Stay / Coordinate–Switch-Partner / Coordinate–Switch-New / Don’t Coordinate–Stay / Don’t Coordinate–Switch-New>
    Reason: <A short explanation why you feel this way about{other_agent.name} (2 sentences max)>
    ChoiceJustification: <short explanation>

    """


FIELD_PATTERNS = {
    "restaurant": [r"Restaurant"],
    "reveal": [r"PersonaReveal", r"Reveal"],
    "justification": [r"ChoiceJustification", r"ChoiceJustify", r"ChoiceExplanation"],
    "intent": [r"Intent", r"Reason"],
}


def extract_field(text, keys):
    for key in keys:
        pattern = rf"{key}\s*:\s*(.*?)(?:;|\n|$)"
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            return m.group(1).strip()
    return ""


def parse_choice(text):
    rest = extract_field(text, FIELD_PATTERNS["restaurant"])
    reveal = extract_field(text, FIELD_PATTERNS["reveal"])
    justification = extract_field(text, FIELD_PATTERNS["justification"])
    return rest, reveal, justification


def parse_intent(text):
    intent = extract_field(text, FIELD_PATTERNS["intent"])
    reason = extract_field(text, ["Reason"])
    return intent, reason


# --------------------------------------------------
# Prepare Simulation Log
# --------------------------------------------------
safe_model_name = model_name.replace(".", "").replace(":", "")
os.makedirs("./different_survey", exist_ok=True)
log_filename = (
    f"./different_survey/{safe_model_name}_alice-{alice_ideology}_jack-{jack_ideology}_run-{run_num}_"
    f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
)
with open(log_filename, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Round", "Choice_A", "Choice_B", "Intent_A", "Intent_B",
        "Reason_A", "Reason_B", "Reveal_A", "Reveal_B",
        "Justification_A", "Justification_B", "Reward_A", "Reward_B"
    ])

MAX_ROUNDS = 25
random.seed(42)
history1, history2 = [], []
available_restaurants = restaurant_names.copy()
last_reward1, last_reward2 = None, None

# For coordination percentage across all decision rounds (including init)
coord_together_count = 0
total_decision_rounds = MAX_ROUNDS + 1  # init round (0) + MAX_ROUNDS

# --------------------------------------------------
# Unified Survey File Setup (one file for Alice+Jack, pre+post)
# --------------------------------------------------
survey_filename = create_survey_filename(model_name, alice_ideology, jack_ideology, run_num)
init_survey_file(survey_filename)

# --------------------------------------------------
# PRE-SURVEY (before simulation)
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
# Simulation Initialization
# --------------------------------------------------
conversation = [
    f"Alice_Political_View: {posts1}",
    f"Jackie_Political_View: {posts2}",
]

prompt1 = build_intent_and_choice_prompt(
    agent1, agent2, available_restaurants, "\n".join(conversation), last_reward1
)
user_proxy.send(recipient=agent1, message=prompt1)
init_reply1 = agent1.last_message()["content"].strip()
init_rest1, init_reveal1, init_just1 = parse_choice(init_reply1)
intent1_init, reason1_init = parse_intent(init_reply1)

prompt2 = build_intent_and_choice_prompt(
    agent2, agent1, available_restaurants, "\n".join(conversation), last_reward2
)
user_proxy.send(recipient=agent2, message=prompt2)
init_reply2 = agent2.last_message()["content"].strip()
init_rest2, init_reveal2, init_just2 = parse_choice(init_reply2)
intent2_init, reason2_init = parse_intent(init_reply2)

history1.append(init_rest1)
history2.append(init_rest2)
conversation.extend([
    f"Alice: {init_rest1}: {init_reveal1}",
    f"Jackie: {init_rest2}: {init_reveal2}"
])

# Count coordination in init round (round 0)
if (
    init_rest1 == init_rest2
    and intent1_init.startswith("Coordinate")
    and intent2_init.startswith("Coordinate")
):
    coord_together_count += 1

with open(log_filename, "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        0, init_rest1, init_rest2, intent1_init, intent2_init,
        reason1_init, reason2_init, init_reveal1, init_reveal2,
        init_just1, init_just2, None, None
    ])

current_init1, current_init2 = init_rest1, init_rest2

# --------------------------------------------------
# Iterative Rounds
# --------------------------------------------------
for r in range(1, MAX_ROUNDS + 1):
    # Small talk
    st_prompt1 = build_small_talk_prompt(agent1, agent2, "\n".join(conversation[-10:]))
    user_proxy.send(recipient=agent1, message=st_prompt1)
    st_reply1 = agent1.last_message()["content"].strip()
    reveal1 = extract_field(st_reply1, FIELD_PATTERNS["reveal"]) or st_reply1[:200]

    st_prompt2 = build_small_talk_prompt(agent2, agent1, "\n".join(conversation[-10:]))
    user_proxy.send(recipient=agent2, message=st_prompt2)
    st_reply2 = agent2.last_message()["content"].strip()
    reveal2 = extract_field(st_reply2, FIELD_PATTERNS["reveal"]) or st_reply2[:200]

    # Intent & choice
    prompt1 = build_intent_and_choice_prompt(
        agent1, agent2, available_restaurants, "\n".join(conversation[:]), last_reward1
    )
    user_proxy.send(recipient=agent1, message=prompt1)
    reply1 = agent1.last_message()["content"].strip()
    rest1, _, just1 = parse_choice(reply1)
    intent1, r1 = parse_intent(reply1)

    prompt2 = build_intent_and_choice_prompt(
        agent2, agent1, available_restaurants, "\n".join(conversation[:]), last_reward2
    )
    user_proxy.send(recipient=agent2, message=prompt2)
    reply2 = agent2.last_message()["content"].strip()
    rest2, _, just2 = parse_choice(reply2)
    intent2, r2 = parse_intent(reply2)

    conversation.extend([
        f"Alice: {rest1}: {reveal1}",
        f"Jackie: {rest2}: {reveal2}"
    ])

    reward1, reward2 = calculate_payoffs(
        rest1, rest2, current_init1, current_init2, intent1, intent2
    )
    last_reward1, last_reward2 = reward1, reward2
    current_init1, current_init2 = rest1, rest2

    if rest1 == rest2 and intent1.startswith("Coordinate") and intent2.startswith("Coordinate"):
        coordinated_restaurants.add(rest1)
        coord_together_count += 1

    with open(log_filename, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            r, rest1, rest2, intent1, intent2, r1, r2,
            reveal1, reveal2, just1, just2, reward1, reward2
        ])

print(f"\nSimulation complete. Log saved to: {log_filename}")

# --------------------------------------------------
# POST-SURVEY
# --------------------------------------------------
print("\n=== Running POST-SURVEY for Alice and Jackie ===")

conversation_history_text = "\n".join(conversation)

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
