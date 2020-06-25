from airdialogue.context_generator.src import utils

class Bot:
  def __init__(self, fact_obj=None, fix_resp_candidate=True):
    self.fix_resp_candidate = fix_resp_candidate
    self.fact_obj = fact_obj
    assert fact_obj is not None
    
  def get_template(self, list_of_templates):
    if self.fix_resp_candidate:
      choice = 0
    else:
      choice = utils.choice(len(list_of_templates))
    return list_of_templates[choice]

  def generate_utterence(self, utterance):
    raise NotImplementedError("need to be implemented in subclasses."
                              "It should return a new utterance, and emit a terminal signal")

class UserBot(Bot):
  greeting_templates = [
      "Hello.",
      "Hello, there.",
      "Hi.",
      "Hey!"
      'Hey there.',
  ]
  greeting_response_how_templates = [
      "I am fine. Thanks for asking.",
      "I am good. Thank you.",
  ]
  def __init__(self, customer_condition, **kargs):
    super().__init__(**kargs)
    self.customer_condition = customer_condition

  def generate_utterence(self, utterance):
    if len(utterance) == 0:
        # Say Hi
        new_utter = self.get_template(self.greeting_templates)
        finished=False
    elif len(utterance) == 1:
        # Reponse to Hi
        if 'how' not in utterance[-1].lower():
            new_utter = self.get_template(self.greeting_templates)
        else:
            new_utter = self.get_template(self.greeting_response_how_templates)
        finished=False
        # Response to Hi
    elif 
        
    return utterance+["agent: "+new_utter], finished
    

class AgentBot(Bot):
  greeting_templates = [
      "Hello.",
      "Hello, there.",
      "Hi.",
      'Hey, how are you.',
      'How is it going?',
      'Hey there.',
  ]
  agent_ask = ['How can I help you today?', 'What can I do for you today?']
  def __init__(self, airfare_database, reservation, **kargs):
    super().__init__(**kargs)
    self.airfare_database = airfare_database
    self.reservation = reservation
    
        
class AgentBot_L5(AgentBot):
  # The best Agent Bot
  def generate_utterence(self, utterance):
    if len(utterance) == 0:
        # Say Hi
        new_utter = self.get_template(self.greeting_templates)
        finished=False
    elif len(utterance) == 1:
        # ask for request
        new_utter = self.get_template(self.agent_ask)
        finished=False
        
    return utterance+["agent: "+new_utter], finished
    