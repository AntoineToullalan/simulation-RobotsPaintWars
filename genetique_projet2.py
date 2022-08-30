

from pyroborobo import Pyroborobo, Controller, AgentObserver, WorldObserver, CircleObject, SquareObject, MovableObject
# from custom.controllers import SimpleController, HungryController
import numpy as np
import random,math,statistics

import paintwars_arena

# =-=-=-=-=-=-=-=-=-= NE RIEN MODIFIER *AVANT* CETTE LIGNE =-=-=-=-=-=-=-=-=-=

def get_extended_sensors(sensors):
    for key in sensors:
        sensors[key]["distance_to_robot"] = 1.0
        sensors[key]["distance_to_wall"] = 1.0
        if sensors[key]["isRobot"] == True:
            sensors[key]["distance_to_robot"] = sensors[key]["distance"]
        else:
            sensors[key]["distance_to_wall"] = sensors[key]["distance"]
    return sensors
    
simulation_mode = 2

posInit1 = (64,232)
posInit2 = (64,288)
posInit3 = (64,344)
posInit4 = (64,400)


maxEvaluations = 1000
bestScore=0
score=0
scores=[]
robotIdMarqueur=-1
ite=0
iteBest=0

def fonction_score(position,liste_place):
    if (int(position[0]),int(position[1])) in liste_place:
        return 0
    return 1

#a partir de 1 parent, on génère 5 enfants avec un bit-flip
def genere_enfants(parent):
    enfants=[parent.copy() for _ in range(5)] 
    deja_modifie=[]
    for enfant in enfants:
        bit_a_modifie=random.randint(0,13) 
        while(bit_a_modifie in deja_modifie):
            bit_a_modifie=random.randint(0,13)
        choix=[-1,0,1] 
        choix.remove(parent[bit_a_modifie]) 
        enfant[bit_a_modifie]=random.choice(choix)
        deja_modifie.append(bit_a_modifie)
    #print(parent,enfants)
    return enfants
    
#on prend les 20 meilleurs paramètres parmi la population de 100 paramètres
def nouvelle_pop(meilleursParents):
    nouvelle_pop=[]
    for parent in meilleursParents:
        nouvelle_pop+=genere_enfants(parent)
    return nouvelle_pop

def pop_initiale(taille):

    res=[]
    for _ in range(taille):
        res.append([random.randint(-1,1) for _ in range(14)])
    return res
    
def nouvelle_generation(scores,pop):
    meilleurs_parents=[[] for _ in range(10)]
    meilleurs_scores=[0 for _ in range(10)]
    for i in range(len(pop)):
        minimum=min(meilleurs_scores)
        a_eliminer=meilleurs_scores.index(minimum)
        if(scores[i]>minimum):
            meilleurs_scores[a_eliminer]=scores[i]
            meilleurs_parents[a_eliminer]=pop[i]
    return nouvelle_pop(meilleurs_parents)
    
#pour savoir quand arrêter l'apprentissage, on regarde la valeur de la médiane dans la liste des scores
def convergence(scores):
    return statistics.stdev(scores)<1000
    
def step(robotId, sensors,position): 
    global param, bestScore, scores,score, bestParam,liste_place,robotIdMarqueur,population,indice,ite,iteBest
    if(robotIdMarqueur == -1):
        robotIdMarqueur=robotId
    taillePop=50
    sensors = get_extended_sensors(sensors)
    if robotId==robotIdMarqueur and rob.iterations % 2000 == 0 and ite<maxEvaluations: 
        liste_place=[] 
        if(rob.iterations==0):
            population=pop_initiale(taillePop)
            indice=0
            bestParam=population[0]
        elif(indice<=taillePop):
            scores.append(score)
            if(score>bestScore):
                bestParam=param
                bestScore=score
                iteBest=ite
            print(bestParam,iteBest,bestScore)
            
            score=0
            if(indice==taillePop):
                print("Nouvelle Génération")
                if(convergence(scores)):
                    print("La convergence a été atteinte !")
                    print("Les meilleurs paramètres sont : ",bestParam," avec un score de ",bestScore)   
                    exit()
                population=nouvelle_generation(scores,population)
                print(population)
                indice=0
                scores=[] 
        
        param=population[indice]
        indice+=1
        
        k=0
        for pos in [posInit1,posInit2,posInit3,posInit4]:
           rob.controllers[k].set_position(pos[0], pos[1])
           rob.controllers[k].set_absolute_orientation(0)
           k+=1 
        ite+=1  

    elif(robotId==robotIdMarqueur and rob.iterations % 2000 == 0 and ite>=maxEvaluations):
        print("Le nombre maximal d'évaluations a été atteint !")
        print("Les meilleurs paramètres sont : ",bestParam," avec un score de ",bestScore)   
        exit()
            
            
    # fonction de contrôle (qui dépend des entrées sensorielles, et des paramètres)
    translation=param[0]
    rotation=param[7]
    i=1
    for key in ["sensor_front_left","sensor_front","sensor_front_right"]:
        translation+=(param[i]*sensors[key]["distance_to_wall"] + param[i+1]*sensors[key]["distance_to_robot"])
        rotation+=(param[7+i]*sensors[key]["distance_to_wall"] + param[7+i+1]*sensors[key]["distance_to_robot"])
        i+=2
    translation = math.tanh(translation)
    rotation = math.tanh(rotation)
    score+=fonction_score(position,liste_place)
    liste_place.append((int(position[0]),int(position[1])))
    return translation, rotation

# =-=-=-=-=-=-=-=-=-= NE RIEN MODIFIER *APRES* CETTE LIGNE =-=-=-=-=-=-=-=-=-=

number_of_robots = 4  # 8 robots identiques placés dans l'arène

arena = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

rob = 0

offset_x = 36
offset_y = 36
edge_width = 28
edge_height = 28


class MyController(Controller):

    def __init__(self, wm):
        super().__init__(wm)

    def reset(self):
        return

    def step(self):

        sensors = {}

        self.get_robot_id_at(0) != -1
        sensors["sensor_left"] = {"distance": self.get_distance_at(0), "isRobot": self.get_robot_id_at(0) != -1}
        sensors["sensor_front_left"] = {"distance": self.get_distance_at(1), "isRobot": self.get_robot_id_at(1) != -1}
        sensors["sensor_front"] = {"distance": self.get_distance_at(2), "isRobot": self.get_robot_id_at(2) != -1}
        sensors["sensor_front_right"] = {"distance": self.get_distance_at(3), "isRobot": self.get_robot_id_at(3) != -1}
        sensors["sensor_right"] = {"distance": self.get_distance_at(4), "isRobot": self.get_robot_id_at(4) != -1}
        sensors["sensor_back_right"] = {"distance": self.get_distance_at(5), "isRobot": self.get_robot_id_at(5) != -1}
        sensors["sensor_back"] = {"distance": self.get_distance_at(6), "isRobot": self.get_robot_id_at(6) != -1}
        sensors["sensor_back_left"] = {"distance": self.get_distance_at(7), "isRobot": self.get_robot_id_at(7) != -1}

        translation, rotation = step(self.id, sensors,self.absolute_position)

        self.set_translation(translation)
        self.set_rotation(rotation)

    def check(self):
        # print (self.id)
        return True


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class MyAgentObserver(AgentObserver):
    def __init__(self, wm):
        super().__init__(wm)
        self.arena_size = Pyroborobo.get().arena_size

    def reset(self):
        super().reset()
        return

    def step_pre(self):
        super().step_pre()
        return

    def step_post(self):
        super().step_post()
        return


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class MyWorldObserver(WorldObserver):
    def __init__(self, world):
        super().__init__(world)
        rob = Pyroborobo.get()

    def init_pre(self):
        super().init_pre()

    def init_post(self):
        global offset_x, offset_y, edge_width, edge_height, rob

        super().init_post()

        for i in range(len(arena)):
            for j in range(len(arena[0])):
                if arena[i][j] == 1:
                    block = BlockObject()
                    block = rob.add_object(block)
                    block.soft_width = 0
                    block.soft_height = 0
                    block.solid_width = edge_width
                    block.solid_height = edge_height
                    block.set_color(164, 128, 0)
                    block.set_coordinates(offset_x + j * edge_width, offset_y + i * edge_height)
                    retValue = block.can_register()
                    # print("Register block (",block.get_id(),") :", retValue)
                    block.register()
                    block.show()

        counter = 0
        for robot in rob.controllers:
            x = 260 + counter*40
            y = 400
            robot.set_position(x, y)
            counter += 1

    def step_pre(self):
        super().step_pre()

    def step_post(self):
        super().step_post()


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class Tile(SquareObject):  # CircleObject):

    def __init__(self, id=-1, data={}):
        super().__init__(id, data)
        self.owner = "nobody"

    def step(self):
        return

    def is_walked(self, id_):
        return


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class BlockObject(SquareObject):
    def __init__(self, id=-1, data={}):
        super().__init__(id, data)

    def step(self):
        return

    def is_walked(self, id_):
        return


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

def main():
    global rob

    rob = Pyroborobo.create(
        "config/paintwars.properties",
        controller_class=MyController,
        world_observer_class=MyWorldObserver,
        #        world_model_class=PyWorldModel,
        agent_observer_class=MyAgentObserver,
        object_class_dict={}
        ,override_conf_dict={"gInitialNumberOfRobots": number_of_robots} # defined in paintwars_config
    )

    rob.start()

    rob.update(1000000)
    rob.close()

if __name__ == "__main__":
    main()



