#!/usr/bin/env python3

import random
import pandas as pd

class dice_game():

    def __init__(self, outside=[], inside=[]):
        
        self.dice_faces = ['black', 'red', 'J', 'Q', 'K', 'A']
        self.rank = {'A':6, 'K':5, 'Q':4, 'J':3, 'red':2, 'black':1}
        self.play_rank  = {'single':1, 'pair':10, 'pair_2':100, 'tripple':1000, 'full':10000,'poker':100000, 'repoker':1000000}
        self.outside = outside
        self.inside  = inside
        self.play = self.outside + self.inside
        self.dict_play = self.check_play(self.play)
        self.trust_previous_player = 0.2

    def check_play(self, play=None):
        if play==None:
            play = self.play # default

        dictionary = {}
        for card in play:
            if not card in dictionary:
                dictionary[card] = 1
            else: 
                dictionary[card] = dictionary[card] + 1
        return dictionary

    def lie(self, value_to_beat, outside):   
        my_value = 0
        len_inside = 5- len(outside)

        while my_value < value_to_beat:
            play = outside + self.throw_cubilete(len_inside)
            my_value, _,__ = self.get_value(play)
        return my_value, play, __
        

    
    def get_value(self, play_given=None):
        """ Give a numerical value to the given play """

        if play_given == None:
            play_given = self.play

        rank = self.rank
        play_rank = self.play_rank
        dictionary = self.check_play(play_given)

        dict_values = dictionary.values()
        highest_play = max(dict_values)
        max_key = max(dictionary, key=dictionary.get)

        play_points = 0
        play_name = ""
        play_type = ""
        to_the = ""
        pair_name1 = ""
        pair_name2 = ""


        # single
        dict_single= [k for k,v in dictionary.items() if float(v) == 1]
        # find the highest valued card
        if len(dict_single) == 0:
            play_name = "nothing yet"
        else:
            play_type="single"
            for card in rank:
                if card in dict_single:
                    # print("Highest is", card)
                    to_the = card
                    play_name = "Only a "+card
                    play_points+=(rank[card]*play_rank['single'])
                    break


        # pairs
        dict_pairs = [k for k,v in dictionary.items() if float(v) == 2]
        if len(dict_pairs) == 1:
            for card in rank:
                if card in dict_pairs:
                    play_points+=(rank[card]*play_rank['pair'])
                    play_type = "pair"
                    play_name = "pair of "+card+"'s to the "+to_the
                    pair_name = card


        elif len(dict_pairs) == 2:
            iteration = 0
            for card in rank:
                if card in dict_pairs:
                    iteration += 1
                    if iteration == 1:
                        play_points+=(rank[card]*play_rank['pair_2'])
                        pair_name1 = card
                    elif iteration == 2:
                        play_points+=(rank[card]*play_rank['pair'])
                        pair_name2 = card
                    play_type = "double_pair"
                    play_name = "double pair of "+ pair_name1 +"'s and "+pair_name2 +"'s to the " + to_the

        # tripple
        dict_tripple = [k for k,v in dictionary.items() if float(v) == 3]
        for value in dict_tripple:
            # there is only one iteration
            play_points+=(rank[value]*play_rank['tripple'])
            tripple_name = value
            if to_the == "":
                play_name = "tripple of " +tripple_name+"'s to the black"
            else:
                play_name = "tripple of " +tripple_name+"'s to the " + to_the
            # full
            if play_type == "pair":
                play_points+=play_rank['full']
                play_type = "full"
                play_name = "full of "+tripple_name+"'s and "+pair_name + "'s"
            else:
                play_type = "tripple"


        # poker
        dict_poker = [k for k,v in dictionary.items() if float(v) == 4]
        for value in dict_poker:
            # there is only one iteration
            play_points+=(rank[value]*play_rank['poker'])
            play_type = "poker"
            play_name = "poker of "+value+ "'s to the "+ to_the


        # poker
        dict_repoker = [k for k,v in dictionary.items() if float(v) == 5]
        # there is a repoker
        for value in dict_repoker:
            # there is only one iteration
            play_points+=(rank[value]*play_rank['repoker'])
            play_type = "repoker"
            play_name = "repoker of "+value +"'s"

        return play_points, play_type, play_name

    def how_good_is_the_throw(self, outside, to_beat, iterations=100000):
        """ 
        Give what you see on the outside and what your oponent claims it has (calculated score).
        Returns how likely it is that that event is true.

        If it returns 0.8 the play is not very good
        If it returns 0.2 the play is very good
        """
        num_outside = len(outside)
        num_inside = 5 - num_outside
        win = 0

        for i in range(iterations):
            supposed_play = outside + self.throw_cubilete(num_inside)
            value, _, __ = self.get_value(supposed_play)
            if value>=to_beat:
                win +=1
        
        probability = win/iterations
        return probability


    def simulation(self, value_to_beat, play, iterations=100000):
        """ Run simulations to know how many dice should be taken
        Select a random number between between 1-5.
        Take that number of dices in the cup and throw it.
        Does that throw beat the current value?
        Repeat the process. The most likely outcome to be able to beat it will be returned, 
        Along with its probability.

        Example: 
        You have A A J J black
        Which dice should you take in order to beat the current play?
        The value of the play is 631
        
        
        Your best chance (depending on the number of iterations) 
        0.7945544554455446 
        black (you should take the black), you have about 80% chance of surpassing it.
        """
        
        # how many dice should be taken?
        random_shuffle = play
        results = {}
        total = {}
        
        for i in range(iterations):
            num_dice_inside = random.randint(1,3)
            random.shuffle(random_shuffle)
            sim_dice_take_inside = random_shuffle[:num_dice_inside]
            sim_dice_outside = random_shuffle[num_dice_inside:]
            sim_dice_inside = self.throw_cubilete(len(sim_dice_take_inside))
            sim_dice_take_inside.sort()
            string = self.listToString(sim_dice_take_inside)

            play_sim = sim_dice_inside + sim_dice_outside
            value, _,__ = self.get_value(play_sim)

            # save results
            if string in total:
                total[string] += 1
            else:
                total[string] = 1

            if value > value_to_beat:        
                if string in results:
                    results[string] += 1
                else:
                    results[string] = 1

        # calculate probability
        percentages = {}
        for result in results:
            percentage = results[result]/total[result]
            percentages[result] = percentage

        # get max and that is the most successfull thing to do!
        percentages_values = percentages.values()
    
        if(len(percentages_values)==0):
            print("impossible to surpass")
        else:
            best_play = max(percentages_values)
            key = max(percentages, key=percentages.get)
            return best_play, key


    def get_me_something_decent(self):
        print("-"*20)
        outside = input("Your outside throw is: ")
        outside = outside.split(" ")
        inside = input("Your inside throw is: ")
        inside = inside.split(" ")
        play = outside +inside
        value,_,name = self.get_value(play)
        probs = self.how_good_is_the_throw(outside,value)

        if probs>0.7:
            # play is among 20% worst plays
            value,_,name = self.lie(value,outside)
        
        print("-> I call", name)
        did_i_lose = input("Did I lose? (y/n)")
        if did_i_lose == 'y':
            return 'm'
        else:
            return 'p'
    
    def adjust_opponents_trust(self, data):
        if data ==  'y':
            self.trust_previous_player += round(random.uniform(0.0, 0.1), 10)
        else:
            self.trust_previous_player -= round(random.uniform(0.0, 0.05), 10)

    def lessed_value_play(self, outside):
        """ The least valued play is every different card starting from black and NOT repeating.
        If it has to repeat it shall be black """
        play_only = outside.copy()
        for face in self.dice_faces:
            if face not in outside:
                play_only.append(face)
                if len(play_only)==5:
                    return play_only

    def how_fucked_am_i_if_they_lied(self, outside, value_claimed, iterations=1000000):
        """ Return 0 if I am really fucked, return 1 if it doesn't really matter 
        If they have lied, what are the chances I surpass the throw. Let's suppose the lowest possible, the 
        opponent doesn't have anything. Then, the value of the play is the value of the outside!
        """
        min_play = self.lessed_value_play(outside)
        percentage,_ = self.simulation(value_claimed, min_play)
        return percentage

    def random_component(self):
        return (random.random()+0.5)/10
        

    def do_i_rise_the_cup(self):
        print("-"*20)
        rise_cup = False
        was_i_right = True
        data = "y"

        outside = input("Opponents outside: ")      
        outside = outside.split(" ")
        inside  = input("Opponents inside : ") 
        inside  = inside.split(" ")

        opp_play = outside + inside
        opp_value, _, __ = self.get_value(opp_play)
        probs = self.how_good_is_the_throw(outside,opp_value)
        will_i_be_ok = self.how_fucked_am_i_if_they_lied(outside,opp_value)
        random_component = self.random_component()
        combined_probability = probs + will_i_be_ok
        mult_probability = probs * will_i_be_ok

        print("Chances play  : ",probs)
        print("Chances fucked: ", will_i_be_ok)
        print("Combined probs: ", combined_probability)
        print("Mult probs    : ", mult_probability)

        if will_i_be_ok < 0.2:
            rise_cup = True

        if(rise_cup):
            print("-> Call lie")
            data = input("Did the person lie? (y/n):" )
            self.adjust_opponents_trust(data)
            if data == 'y':
                return 'p'
            else:
                return 'm'
            
        else:
            print("-> I'll play")
            inside  = input("Real inside : ") 
            inside  = inside.split(" ")
            play = inside + outside
            value, _, __ = self.get_value(play)
            if opp_value > value:
                print("-> The opponent lied")
                data = "y"
            else:
                print("-> The opponent didn't lie")
                data = "n"
            self.adjust_opponents_trust(data)

            percentage, take = self.simulation(opp_value, play)
            print("-"*20)
            print("-> Throw (",take,")")
            print("Percentage win:",percentage)
            take = take.split(" ")
            outside_throw = play.copy()
            for card in take:
                outside_throw.remove(card)
            inside_throw = input("What's inside? ")
            inside_throw = inside_throw.split(" ")
            my_play = outside_throw + inside_throw
            new_value,_,call = self.get_value(my_play)

            if new_value < opp_value:
                # lie
                lie_value, my_play, lie_call = self.lie(opp_value,outside_throw)
                print("Throw:", my_play)
                print("-> I call:",lie_call)
            else:
                print("Throw:", my_play)
                print("-> I call:", call)

        did_i_lose = input("Did I lose? (y/n): ")
        if did_i_lose == 'y':
            return 'm'
        else:
            return 'p'
            

    def main(self):
        print("GAME STARTS")
        who_starts = input("Who goes first? machine(m) person(p): ")

        while(True):
            if who_starts == 'm':
                who_starts = self.get_me_something_decent()
            else:
                who_starts = self.do_i_rise_the_cup()


    # def lineal_lier_detector(self):
        # y = probs_rise_cup
        # x = probs_lie
        # the points of this line is 

        # y = probs_to_rise
        # |   .   .   .   .
        # |   .   .   .   .
        # |   .   .   .   .
        # |   .   .   .   .
        # |.________________ x = probs_i_am_fucked


    def listToString(self,s):  
        str1 = ""     
        for ele in s:  
            str1 += (ele +" ") 
        return str1.strip()

    def throw_cubilete(self, num_dice):
        random_order = self.dice_faces
        cubilete_play = []

        for i in range(num_dice):
            random.shuffle(random_order)
            cubilete_play.append(random_order[0])

        return cubilete_play

    def set_play(self, play):
        self.play = play

    def get_dictionary(self):
        return self.dict_play

    def get_play(self):
        return self.play

if __name__ == "__main__":
    game = dice_game()
    game.main()
