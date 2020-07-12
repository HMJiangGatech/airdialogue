# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This file contains the main dialogue logic."""

from airdialogue.simulator.interaction import *

tgt_agent_turn_prefix = 'agent_tgt:'

class InteractionOPE(Interaction):
  """This class contains the dialogue interaction between the two agents."""

  def tgt_agent_turn(self, utterance):
    return tgt_agent_turn_prefix + ' ' + utterance

  def generate_greetings(self, utterance, speaker):
    """This function generates greets."""
    # skip greeting
    if speaker == 0 and np.random.random() < self.skip_greeting:
      return utterance
    pair = self.get_template(greeting_pairs)
    if speaker == 0:
      utterance.append(self.customer_turn(pair[0]))
      utterance.append(self.agent_turn(pair[1]))
      utterance.append(self.tgt_agent_turn(pair[1]))
    else:
      tgt_pair = self.get_template(greeting_pairs)
      utterance.append(self.agent_turn(pair[0]))
      utterance.append(self.tgt_agent_turn(pair[0]))
      utterance.append(self.customer_turn(pair[1]))
    return utterance

  def generate_agent_ask(self, utterance):
    utterance.append(self.agent_turn(self.get_template(agent_ask)))
    utterance.append(self.tgt_agent_turn(self.get_template(agent_ask)))
    return utterance

  def no_reservation(self, utterance):
    agent_confirm_utt = self.get_template(agent_conclusion_message['no_res'])
    utterance.append(self.agent_turn(agent_confirm_utt))
    agent_confirm_utt = self.get_template(agent_conclusion_message['no_res'])
    utterance.append(self.tgt_agent_turn(agent_confirm_utt))
    return utterance

  def cancel_reservation(self, utterance):
    agent_utt = self.get_template(agent_confirm_change['cancel'])
    utterance.append(self.agent_turn(agent_utt))
    agent_utt = self.get_template(agent_confirm_change['cancel'])
    utterance.append(self.tgt_agent_turn(agent_utt))
    customer_utt = self.get_template(customer_confirm_change['cancel'])
    utterance.append(self.customer_turn(customer_utt))
    agent_confirm_utt = self.get_template(agent_conclusion_message['cancel'])
    utterance.append(self.agent_turn(agent_confirm_utt))
    agent_confirm_utt = self.get_template(agent_conclusion_message['cancel'])
    utterance.append(self.tgt_agent_turn(agent_confirm_utt))
    return utterance

  def fulfill_basic_requirement(self, goal, cus_cond, ag_cond, utterance):
    """This function fulfill bsic requirements."""
    # check departure and return city
    if 'departure_airport' not in ag_cond:
      assert 'return_airport' not in ag_cond
      # print ('goal',goal)
      ask_cities = self.get_template(agent_first_respond[goal]['c1c2'])
      utterance.append(self.agent_turn(ask_cities))
      ask_cities = self.get_template(agent_first_respond[goal]['c1c2'])
      utterance.append(self.tgt_agent_turn(ask_cities))
      depart = cus_cond['departure_airport']
      ret = cus_cond['return_airport']
      respond_cities = self.get_template(customer_first_respond['c1c2']).format(
          depart, ret)
      utterance.append(self.customer_turn(respond_cities))
      ag_cond['departure_airport'] = depart
      ag_cond['return_airport'] = ret
    if 'departure_month' not in ag_cond:
      assert 'departure_day' not in ag_cond
      assert 'return_month' not in ag_cond
      assert 'return_day' not in ag_cond
      ask_date = self.get_template(agent_first_respond[goal]['d1d2'])
      utterance.append(self.agent_turn(ask_date))
      ask_date = self.get_template(agent_first_respond[goal]['d1d2'])
      utterance.append(self.tgt_agent_turn(ask_date))
      d_m, d_d = cus_cond['departure_month'], cus_cond['departure_day']
      a_m, a_d = cus_cond['return_month'], cus_cond['return_day']
      dep = d_m + ' ' + str(d_d)
      ar = a_m + ' ' + str(a_d)
      respond_date = self.get_template(customer_first_respond['d1d2']).format(
          dep, ar)
      utterance.append(self.customer_turn(respond_date))
      ag_cond['departure_month'] = d_m
      ag_cond['departure_day'] = d_d
      ag_cond['return_month'] = a_m
      ag_cond['return_day'] = a_d
    return ag_cond, utterance

  def continue_booking(self, cus_cond, ag_cond, kb, utterance):
    """This function books the flight."""
    goal = ag_cond['goal']
    goal_str = self.fact_obj.goal_str_arr[goal]
    ag_cond, utterance = self.fulfill_basic_requirement(goal_str, cus_cond,
                                                        ag_cond, utterance)
    status = None
    first_time = True
    error = 'basic'
    while not status:
      flight = self.airflight_selector(ag_cond, kb)
      if not flight:  # terminal condition
        utterance.append(
            self.agent_turn(
                self.get_template(agent_conclusion_message['no_flight'])))
        utterance.append(
            self.tgt_agent_turn(
                self.get_template(agent_conclusion_message['no_flight'])))
        if secondary_error:
          status = 'no_flight' '_' + error
        else:
          status = 'no_flight'

        return utterance, status, flight
      else:
        utterance.append(
            self.agent_turn(self.generate_confirmation(flight, first_time)))
        utterance.append(
            self.tgt_agent_turn(self.generate_confirmation(flight, first_time)))
        first_time = False
        condition = utils.check_condition(self.fact_obj, flight, cus_cond)
        msg, ag_cond, error = self.get_message(
            ag_cond, cus_cond, condition)  # will do merge condition within
        utterance.append(self.customer_turn(msg))
        if condition == 'satisfied':
          goal_int = cus_cond['goal']
          status = self.fact_obj.goal_str_arr[goal_int]  # either book or change
    # status is either book, change, or potenitally abort
    ask_confirm = self.get_template(agent_confirm_change[status]).format(
        flight['flight_number'])
    utterance.append(self.agent_turn(ask_confirm))
    utterance.append(self.tgt_agent_turn(ask_confirm))
    regret = np.random.random() < self.regret_prob
    if regret:
      status = 'abort'
    cus_re_conrim = self.get_template(customer_confirm_change[status])
    utterance.append(self.customer_turn(cus_re_conrim))
    agent_conclusion = self.get_template(agent_conclusion_message[status])
    utterance.append(self.agent_turn(agent_conclusion))
    utterance.append(self.tgt_agent_turn(agent_conclusion))
    return utterance, status, flight

  def generate_dialogue(self, customer, knowledge_base, ref_policy_accu=1, tgt_policy_accu=1):
    """This function is the main entry of the dialogue generation logic."""
    airfare_database = knowledge_base.get_json()['kb']
    reservation = knowledge_base.get_json()['reservation']
    utterance = []
    # 0a. decides who speaks first 0--customer, 1--agent
    speaker = 0
    # 0b. generate customer's full condition and agent_condition
    customer_condition = customer.get_customer_condition()
    agent_condition = {}
    # 1. greetings
    utterance = self.generate_greetings(utterance, speaker)
    # 2. generate agent's utterance to ask for request if
    # customer finished the last turn
    if speaker == 1:
      utterance = self.generate_agent_ask(utterance)
    # 3. generate customer request
    utterance, agent_condition, goal_str = self.generate_customer_request(
        customer_condition, agent_condition, utterance)

    # 4 ask for name first
    ask_name_utt = self.get_template(agent_ask_name)
    utterance.append(self.agent_turn(ask_name_utt))
    ask_name_utt = self.get_template(agent_ask_name)
    utterance.append(self.tgt_agent_turn(ask_name_utt))
    answer_name_utt = self.get_template(cutomer_name).format(
        customer_condition['name'].replace('_', ' '))
    utterance.append(self.customer_turn(answer_name_utt))

    # 5. fulfill basic requirement
    # (departure/return city, departure/return month/day)

    modify_tgt_utt = None
    modify_tgt_utt_id = len(utterance)+1

    if goal_str == 'book':
      # randomly corrupt by ref_policy_accu
      _ref_randn = np.random.random()
      _tgt_randn = np.random.random()
      if _ref_randn >= ref_policy_accu and \
         _tgt_randn >= tgt_policy_accu:
        goal_str = 'cancel'
      elif _ref_randn < ref_policy_accu and \
           _tgt_randn < tgt_policy_accu:
        pass
      elif _ref_randn < ref_policy_accu and \
           _tgt_randn >= tgt_policy_accu:
        if reservation == 0:
          modify_tgt_utt = self.get_template(agent_conclusion_message['no_res'])
        else:
          modify_tgt_utt = self.get_template(agent_confirm_change['cancel'])
      elif _ref_randn >= ref_policy_accu and \
           _tgt_randn < tgt_policy_accu:
        assert 'return_airport' not in agent_condition
        modify_tgt_utt = self.get_template(agent_first_respond[goal_str]['c1c2'])
        goal_str = 'cancel'

    if goal_str == 'book' or (goal_str == 'change' and reservation != 0):
      # status can be book, change, no_flight, abort
      utterance, status, flight = self.continue_booking(
          customer_condition, agent_condition, airfare_database, utterance)
    elif goal_str in ['change', 'cancel'] and reservation == 0:
      utterance = self.no_reservation(utterance)
      status = 'no_reservation'
      flight = None
    elif goal_str == 'cancel':
      utterance = self.cancel_reservation(utterance)
      status = 'cancel'
      flight = None
    if modify_tgt_utt is not None:
      utterance[modify_tgt_utt_id] = self.tgt_agent_turn(modify_tgt_utt)

    # per new format we will need to return a flight arr to consider the
    # situation where multiple cheapest flights are available. As in the real
    # data here we only choose at most one flight. However, the
    # expected_action should be able to contain multiple flights.
    flight_arr = []
    if flight:
      flight_arr.append(flight)
    # use the generate action function from utils. It will standarlize
    # the action
    # print(customer_condition['name'])
    name = customer_condition['name'].replace('_', ' ')
    action = utils.generate_action(flight_arr, name, status)

    # print utterance
    return utterance, action, status
