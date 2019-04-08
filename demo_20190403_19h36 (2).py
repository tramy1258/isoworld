#
# World of Isotiles
# Author: nicolas.bredeche(at)sorbonne-universite.fr
#
# Started: 2018-11-17
# purpose: basic code developped for teaching artificial life and ecological simulation at Sorbonne Univ. (SU)
# course: L2, 2i013 Projet, "Vie Artificielle"
# licence: CC-BY-SA
#
# Requirements: Python3, Pygame
#
# Credits for third party resources used in this project:
# - Assets: https://www.kenney.nl/ (great assets by Kenney Vleugels with *public domain license*)
# - https://www.uihere.com/free-cliparts/space-invaders-extreme-2-video-game-arcade-game-8-bit-space-invaders-3996521
#
# Random bookmarks:
# - scaling images: https://stackoverflow.com/questions/43196126/how-do-you-scale-a-design-resolution-to-other-resolutions-with-pygame
# - thoughts on grid worlds: http://www-cs-students.stanford.edu/~amitp/game-programming/grids/
# - key pressed? https://stackoverflow.com/questions/16044229/how-to-get-keyboard-input-in-pygame
# - basic example to display tiles: https://stackoverflow.com/questions/20629885/how-to-render-an-isometric-tile-based-world-in-python
# - pygame key codes: https://www.pygame.org/docs/ref/key.html
# - pygame capture key combination: https://stackoverflow.com/questions/24923078/python-keydown-combinations-ctrl-key-or-shift-key
# - methods to initialize a 2D array: https://stackoverflow.com/questions/2397141/how-to-initialize-a-two-dimensional-array-in-python
# - bug with SysFont - cf. https://www.reddit.com/r/pygame/comments/1fhq6d/pygamefontsysfont_causes_my_script_to_freeze_why/
#       myfont = pygame.font.SysFont(pygame.font.get_default_font(), 16)
#       myText = myfont.render("Hello, World", True, (0, 128, 0))
#       screen.blit(myText, (screenWidth/2 - text.get_width() / 2, screenHeight/2 - text.get_height() / 2))
#       ... will fail.
#
# TODO list
# - double buffer
# - multiple agents


import sys
import datetime
from random import *
import math
import time

import pygame
from pygame.locals import *

###

versionTag = "2018-11-18_23h24"

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# display screen dimensions
screenWidth  = 1400 # 1400
screenHeight = 900 #900

# world dimensions (ie. nb of cells in total)
worldWidth  = 60 #60
worldHeight = 60 #60

# set surface of displayed tiles (ie. nb of cells that are rendered) -- must be superior to worldWidth and worldHeight
viewWidth  = 30 #60
viewHeight = 30 #60

scaleMultiplier = 0.3  # re-scaling of loaded images

objectMapLevels = 12 # number of levels for the objectMap. This determines how many objects you can pile upon one another.

# set scope of displayed tiles
xViewOffset = 0
yViewOffset = -1

addNoise    = False
addWave     = True #True
flow        = False #False
waterfalls  = [False]*4 # check if waterfall exists
flow_height = 6
drops       = 15
water_on_mount = 150
hidden_steps = False

maxFps = 30 # set up maximum number of frames-per-second

verbose = False # display message in console on/off
verboseFps = True # display FPS every once in a while

season = 1 #spring at beginning
last_season = 1
probaFire        = [0.5   ,0.5   ,0.5   ,0]
probaSuddenFire  = [0.0005,0.0005,0.0005,0]
probaTreeGrow    = [0.002 ,0.003 ,0.001 ,0]
probaGrassGrow   = [0.004 ,0.005 ,0.003 ,0]

agents = []
#preys and predators in a same array to create more interesting scenarios (preys can escape)

nbPrey = 30
nbPreda = 10
probaNewTree     = [0.35  ,0.35  ,0.35  ,0.35]
probaPreyBorn    = [0.2   ,0.1   ,0.1   ,0.05]
probaPredBorn    = [0.3   ,0.2   ,0.2   ,0.05]
probaAgentMove   = [1     ,1     ,1     ,1   ]
lifeCyclePrey    = 80
lifeCyclePreda   = 90
lifeCycleDropper = 50

nbTrees = 0 # calculated later
nbHerbs = 0 # calculated later
nbPineTrees = 10 #60

nbCoin = 0
nbKilled = 2

printed = False #debug
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


pygame.init()

pygame.key.set_repeat(5,5)

fpsClock = pygame.time.Clock()

screen = pygame.display.set_mode((screenWidth, screenHeight), DOUBLEBUF)

font = pygame.font.Font('final_data/Pixel Emulator.otf',20)
text_season = [font.render(text[0],True,text[1]) for text in (('spring',(240,128,128)),\
                                                              ('summer',(34 ,139,34 )),\
                                                              ('fall'  ,(218,165,32 )),\
                                                              ('winter',(47 ,79 ,79 )))]

pygame.display.set_caption('World of Isotiles')

###

###

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def loadImage(filename,tileTotalHeight,tileTotalWidth): #loadImage with added width and height to load images of various dimensions
    image = pygame.image.load(filename).convert_alpha()
    image = pygame.transform.scale(image, (int(tileTotalWidth*scaleMultiplier), int(tileTotalHeight*scaleMultiplier)))
    return image

def loadAllImages():
    global tileType, objectType, agentType

    tileType = [
    #(loadImage('path',height,width),
    # width_difference_compared_to_normal_tile,
    # height_difference_compared_to_normal_tile,
    # height_multiplier_tab_indice),
    (loadImage('final_data/cliffBrown_blockQuarterDark_NW.png'  ,72 ,151),0,0,2), #ground for water  #0
    (loadImage('final_data/cliffGrey_blockHalf_NW.png'          ,95 ,151),0,0,1), #ground1_half      #1 
    (loadImage('final_data/cliffGrey_blockQuarter_NW.png'       ,72 ,151),0,0,2), #ground1_quarter   #2 

    (loadImage('final_data/platformerTile_09.png' ,107,151),0,0,0),           #ground3           #3
    (loadImage('final_data/platformerTile_06.png' ,95,151),0,0,0),            #ground1_half snow #4
    (loadImage('final_data/platformerTile_08.png' ,107,151),0,0,0),           #ground3 snow      #5

    (loadImage('final_data/cliffBrown_blockHalf_NW.png'     ,95 ,151),0,0,1),  #ground2_half      #6
    (loadImage('final_data/cliffBrown_blockQuarter_NW.png'  ,72 ,151),0,0,2),  #ground2_quarter   #7
    (loadImage('final_data/blockSnow_NW.png'                ,107,151),0,0,1)   #ground2 snow      #8
    ]

    objectType = []
    #(loadImage('path',height,width),
    # width_difference_compared_to_normal_tile,
    # height_difference_compared_to_normal_tile,
    # height_multiplier_tab_indice),

    objectType.append(None) # default -- never drawn
    objectType.append((loadImage('final_data/tree_small_NW_ret_red.png',107,151),0,0,0))    # burning tree  #1
    objectType.append((loadImage('final_data/campfireStones_rocks_NW.png',72,120),0,0,2))   # ashes         #2
    objectType.append((loadImage('final_data/grass_on_fire2.png',52,39),60,20,0))           # burning grass #3

    objectType.append((loadImage('final_data/tree_oak_dark_NE.png',95,77),45,-5,0)) # oak tree spring      #4
    objectType.append((loadImage('final_data/tree_oak_NE.png'     ,95,77),45,-5,0)) # oak tree summer      #5
    objectType.append((loadImage('final_data/tree_oak_fall_NE.png',95,77),45,-5,0)) # oak tree fall        #6

    objectType.append((loadImage('final_data/tree_thin_dark_SW.png',95,77),45,-5,0)) # tree thin spring #7
    objectType.append((loadImage('final_data/tree_thin_SW.png'     ,95,77),45,-5,0)) # tree thin summer #8
    objectType.append((loadImage('final_data/tree_thin_fall_SW.png',95,77),45,-5,0)) # tree thin fall   #9

    objectType.append((loadImage('final_data/tree_tall_dark_NW.png',85,35),45,-5,0)) # tree tall spring #10
    objectType.append((loadImage('final_data/tree_tall_NW.png'     ,85,35),45,-5,0)) # tree tall summer #11
    objectType.append((loadImage('final_data/tree_tall_fall_NW.png',85,35),45,-5,0)) # tree tall fall   #12

    objectType.append((loadImage('final_data/tree_simple_dark_NW.png',95,50),45,-5,0)) # tree simple spring #13
    objectType.append((loadImage('final_data/tree_simple_NW.png'     ,95,50),45,-5,0)) # tree simple winter #14
    objectType.append((loadImage('final_data/tree_simple_fall_NW.png',95,50),45,-5,0)) # tree simple fall   #15

    objectType.append((loadImage('final_data/tree_pine_tall_detailed_SE.png'  ,95,58),45,-5,0))   # pine tree tall          #16
    objectType.append((loadImage('final_data/tree_pine_short_detailed_NE.png' ,85,57),45,-5,0))   # pine tree short         #17
    objectType.append((loadImage('final_data/tree_pineSmall_round3_NW.png'    ,80,57),45,-5,0))   # pine tree small round3  #18
    objectType.append((loadImage('final_data/tree_pineSmall_round4_NE.png'    ,70,57),45,-5,0))   # pine tree small round4  #19
    objectType.append((loadImage('final_data/tree_pineSmall_round5_NW.png'    ,80,63),45,-5,0))   # pine tree small round5  #20

    objectType.append((loadImage('final_data/flower_red3_NE.png'    ,23,16),45,50,0))   # red flower    #21
    objectType.append((loadImage('final_data/flower_beige3_NE.png'  ,23,16),45,50,0))   # beige flower  #22
    objectType.append((loadImage('final_data/grass_dense_SE.png'    ,30,50),45,50,0))   # grass         #23
    objectType.append((loadImage('final_data/plant_bush_SE.png'         ,30,32),45,50,0))  # plant bush          #24
    objectType.append((loadImage('final_data/plant_bushDetailed_SE.png' ,51,47),45,50,0))  # plant bush detailed #25
    objectType.append((loadImage('final_data/mushroom_redGroup_SE.png'   ,33,28),45,50,0)) # mushroom            #26

    objectType.append((loadImage('final_data/treePineSnowRound_NE.png' ,80,63),45,-5,0))   # pine tree short half snowed  #27
    objectType.append((loadImage('final_data/treePineSnowRound.png'    ,95,58),45,-5,0))   # pine tree tall half snowed   #28
    objectType.append((loadImage('final_data/treePineSnowedFull_SW.png',80,63),45,-5,0))   # pine tree short full snowed  #29
    objectType.append((loadImage('final_data/treePineSnowedFull.png'   ,95,58),45,-5,0))   # pine tree tall full snowed   #30
    objectType.append((loadImage('final_data/treeSnow_NW.png'          ,95,77),45,-5,0))   # tree full snowed             #31

    objectType.append((loadImage('final_data/cliffGrey_blockHalf_NW.png'      ,95 ,151),0,0,1))  #ground2 half    #32 
    objectType.append((loadImage('final_data/cliffGrey_block_NW.png'          ,107,151),0,0,0))  #ground2         #33
    objectType.append((loadImage('final_data/cliffGrey_blockQuarter_NW.png'   ,72 ,151),0,0,2))  #ground2 quarter #34
    objectType.append((loadImage('final_data/platformerTile_12.png'           ,107,151),0,0,0))  #ground1 snow    #35


    objectType.append((loadImage('final_data/cliffBrown_cornerInnerTop_SE.png',89 ,151),0,0,0))  #brown corner rectangular edge SE #36
    objectType.append((loadImage('final_data/cliffBrown_cornerInnerTop_SW.png',107,110),41,0,0)) #brown corner rectangular edge SW #37
    objectType.append((loadImage('final_data/cliffBrown_cornerInnerTop_NE.png',89 ,151),0,21,0)) #brown corner rectangular edge NE #38
    objectType.append((loadImage('final_data/cliffBrown_cornerInnerTop_NW.png',107,110),0,0,0))  #brown corner rectangular edge NW #39

    objectType.append((loadImage('final_data/cliffGrey_cornerInnerTop_SE.png',89 ,151),0,0,0))  #grey corner rectangular edge SE #40
    objectType.append((loadImage('final_data/cliffGrey_cornerInnerTop_SW.png',107,110),41,0,0)) #grey corner rectangular edge SW #41
    objectType.append((loadImage('final_data/cliffGrey_cornerInnerTop_NE.png',89 ,151),0,21,0)) #grey corner rectangular edge NE #42
    objectType.append((loadImage('final_data/cliffGrey_cornerInnerTop_NW.png',107,110),0,0,0))  #grey corner rectangular edge SW #43

    objectType.append((loadImage('final_data/cliffBrown_top_SE.png'           ,89,110),0,0,0))   #brown edge top SE #44
    objectType.append((loadImage('final_data/cliffBrown_top_SW.png'           ,89,110),41,0,0))  #brown edge top SW #45
    objectType.append((loadImage('final_data/cliffBrown_top_NE.png'           ,89,110),41,21,0)) #brown edge top NE #46
    objectType.append((loadImage('final_data/cliffBrown_top_NW.png'           ,89,110),0,21,0))  #brown edge top NW #47

    objectType.append((loadImage('final_data/cliffGrey_top_SE.png'            ,89,110),0,0,0))   #grey edge top SE #48
    objectType.append((loadImage('final_data/cliffGrey_top_SW.png'            ,89,110),41,0,0))  #grey edge top SW #49
    objectType.append((loadImage('final_data/cliffGrey_top_NE.png'            ,89,110),41,21,0)) #grey edge top NE #50
    objectType.append((loadImage('final_data/cliffGrey_top_NW.png'            ,89,110),0,21,0))  #grey edge top NW #51

    objectType.append((loadImage('final_data/cliffGrey_cornerInnerMid_SE.png' ,89 ,151),0,0,0))  #grey corner rectangular edge mid SE #52
    objectType.append((loadImage('final_data/cliffGrey_cornerInnerMid_SW.png' ,107,110),41,0,0)) #grey corner rectangular edge mid SW #53
    objectType.append((loadImage('final_data/cliffGrey_cornerInnerMid_NE.png' ,89 ,151),0,21,0)) #grey corner rectangular edge mid NE #54
    objectType.append((loadImage('final_data/cliffGrey_cornerInnerMid_NW.png' ,107,110),0,0,0))  #grey corner rectangular edge mid NW #55
    
    objectType.append((loadImage('final_data/cliffGrey_SE.png'                ,89,110),0,0,0))   #grey edge mid SE #56
    objectType.append((loadImage('final_data/cliffGrey_SW.png'                ,89,110),41,0,0))  #grey edge mid SW #57
    objectType.append((loadImage('final_data/cliffGrey_NE.png'                ,89,110),41,21,0)) #grey edge mid NE #58
    objectType.append((loadImage('final_data/cliffGrey_NW.png'                ,89,110),0,21,0))  #grey edge mid NW #59

    objectType.append((loadImage('final_data/ground_dirtRiverWater_NW.png'    ,72,151),0,0,2))     #active water    #60
    objectType.append((loadImage('final_data/ground_dirtRiverWater_NW.png'    ,72,151),0,0,2))     #static water    #61
################################################################################################################################# minus 12
    objectType.append((loadImage('final_data/cliffBrown_waterfallTop_SE.png'  ,89,110),0,0,0))   #brown waterfall top SE #74
    objectType.append((loadImage('final_data/cliffBrown_waterfallTop_SW.png'  ,89,110),41,0,0))  #brown waterfall top SW #75
    objectType.append((loadImage('final_data/cliffBrown_waterfallTop_NE.png'  ,89,110),41,21,0)) #brown waterfall top NE #76
    objectType.append((loadImage('final_data/cliffBrown_waterfallTop_NW.png'  ,89,110),0,21,0))  #brown waterfall top NW #77

    objectType.append((loadImage('final_data/cliffGrey_waterfallTop_SE.png'  ,89,110),0,0,0))   #grey waterfall top SE #78
    objectType.append((loadImage('final_data/cliffGrey_waterfallTop_SW.png'  ,89,110),41,0,0))  #grey waterfall top SW #79
    objectType.append((loadImage('final_data/cliffGrey_waterfallTop_NE.png'  ,89,110),41,21,0)) #grey waterfall top NE #80
    objectType.append((loadImage('final_data/cliffGrey_waterfallTop_NW.png'  ,89,110),0,21,0))  #grey waterfall top NW #81

    objectType.append((loadImage('final_data/cliffGrey_waterfallMid_SE.png'  ,89,110),0,0,0))   #grey waterfall mid SE #82
    objectType.append((loadImage('final_data/cliffGrey_waterfallMid_SW.png'  ,89,110),41,0,0))  #grey waterfall mid SW #83
    objectType.append((loadImage('final_data/cliffGrey_waterfallMid_NE.png'  ,89,110),41,21,0)) #grey waterfall mid NE #84
    objectType.append((loadImage('final_data/cliffGrey_waterfallMid_NW.png'  ,89,110),0,21,0))  #grey waterfall mid NW #85

    objectType.append((loadImage('final_data/ground_dirtRiverSideCorner_SE.png',72,151),0,0,2))    #riverSideCorner_SE #86
    objectType.append((loadImage('final_data/ground_dirtRiverSideCorner_SW.png',72,151),0,0,2))    #riverSideCorner_SW #87
    objectType.append((loadImage('final_data/ground_dirtRiverSideCorner_NE.png',72,151),0,0,2))    #riverSideCorner_NE #88
    objectType.append((loadImage('final_data/ground_dirtRiverSideCorner_NW.png',72,151),0,0,2))    #riverSideCorner_NW #89

    objectType.append((loadImage('final_data/ground_dirtRiverCornerInner_SE.png',72,151),0,0,2))    #riverInnerCorner_SE #90
    objectType.append((loadImage('final_data/ground_dirtRiverCornerInner_SW.png',72,151),0,0,2))    #riverInnerCorner_SW #91
    objectType.append((loadImage('final_data/ground_dirtRiverCornerInner_NE.png',72,151),0,0,2))    #riverInnerCorner_NE #92
    objectType.append((loadImage('final_data/ground_dirtRiverCornerInner_NW.png',72,151),0,0,2))    #riverInnerCorner_NW #93

    objectType.append((loadImage('final_data/ground_dirtRiverSide_SE.png',72,151),0,0,2))    #riverSide_SE #94
    objectType.append((loadImage('final_data/ground_dirtRiverSide_SW.png',72,151),0,0,2))    #riverSide_SW #95
    objectType.append((loadImage('final_data/ground_dirtRiverSide_NE.png',72,151),0,0,2))    #riverSide_NE #96
    objectType.append((loadImage('final_data/ground_dirtRiverSide_NW.png',72,151),0,0,2))    #riverSide_NW #97

    objectType.append((loadImage('final_data/ground_dirtRiverEntrance_SE.png',72,151),0,0,2))    #riverEntrance_SE #98
    objectType.append((loadImage('final_data/ground_dirtRiverEntrance_SW.png',72,151),0,0,2))    #riverEntrance_SW #99
    objectType.append((loadImage('final_data/ground_dirtRiverEntrance_NE.png',72,151),0,0,2))    #riverEntrance_NE #100
    objectType.append((loadImage('final_data/ground_dirtRiverEntrance_NW.png',72,151),0,0,2))    #riverEntrance_NW #101

    objectType.append((loadImage('final_data/ground_dirtRiverEnd_SE.png',72,151),0,0,2))    #riverEnd_SE #102
    objectType.append((loadImage('final_data/ground_dirtRiverEnd_SW.png',72,151),0,0,2))    #riverEnd_SW #103
    objectType.append((loadImage('final_data/ground_dirtRiverEnd_NE.png',72,151),0,0,2))    #riverEnd_NE #104
    objectType.append((loadImage('final_data/ground_dirtRiverEnd_NW.png',72,151),0,0,2))    #riverEnd_NW #105

    objectType.append((loadImage('final_data/ground_dirtRiverCorner_SE.png',72,151),0,0,2)) #riverCorner_SE #106
    objectType.append((loadImage('final_data/ground_dirtRiverCorner_SW.png',72,151),0,0,2)) #riverCorner_SW #107
    objectType.append((loadImage('final_data/ground_dirtRiverCorner_NE.png',72,151),0,0,2)) #riverCorner_NE #108
    objectType.append((loadImage('final_data/ground_dirtRiverCorner_NW.png',72,151),0,0,2)) #riverCorner_NW #109

    objectType.append((loadImage('final_data/cliffGrey_steps_SE.png',107,151),0,0,0)) # grey steps_SE #110
    objectType.append((loadImage('final_data/cliffGrey_steps_SW.png',107,151),0,0,0)) # grey steps_SW #111
    objectType.append((loadImage('final_data/cliffGrey_steps_NE.png',107,151),0,0,0)) # grey steps_NE #112
    objectType.append((loadImage('final_data/cliffGrey_steps_NW.png',107,151),0,0,0)) # grey steps_NW #113    

    objectType.append((loadImage('final_data/coinGold_SE.png',54,46),70,30,0)) # coin_SE #114
    objectType.append((loadImage('final_data/coinGold_SW.png',54,46),70,30,0)) # coin_SW #115
    objectType.append((loadImage('final_data/coinGold_NE.png',54,46),70,30,0)) # coin_NE #116
    objectType.append((loadImage('final_data/coinGold_NW.png',54,46),70,30,0)) # coin_NW #117

    objectType.append((loadImage('final_data/ground_dirt_NW.png'              ,72,151),0,0,2)) # riverdirt   #118
    objectType.append((loadImage('final_data/ground_dirtRiverTile_NW.png'     ,72,151),0,0,2)) # riverTile   #119
    objectType.append((loadImage('final_data/stone_tall2_NE.png'   ,350,330),-50,-260,0))      # rock        #120
    objectType.append((loadImage('final_data/snowmanFancy_SW.png'  ,350,210),-59,-243,0))      # snow man    #121   

##############################################
    agentType  = []
    agentType.append(None) # default -- never drawn

    agentType.append((loadImage('final_data/invader_ret_new.png'   ,107,128),0,0,0)) # invader - predators - newborn #1
    agentType.append((loadImage('final_data/invader_ret.png'       ,107,128),0,0,0)) # invader - predator            #2
    agentType.append((loadImage('final_data/invader_ret_hungry.png',107,128),0,0,0)) # invader - predator - hungry   #3

    agentType.append((loadImage('final_data/ghost_pinky_new.png'   ,107,128),0,0,0)) # pink ghost - prey - new      #4
    agentType.append((loadImage('final_data/ghost_pinky.png'       ,107,128),0,0,0)) # pink ghost - prey            #5
    agentType.append((loadImage('final_data/ghost_pinky_hungry.png',107,128),0,0,0)) # pink ghost - prey - hungry   #6

    agentType.append((loadImage('final_data/ghost.png'      ,107,128),0,0,0)) # purple ghost - dropper              #7

    agentType.append((loadImage('final_data/player2.png'    ,107,128),0,0,0))   # player                              #8

def resetImages():
    global tileTotalWidth, tileTotalHeight, scaleMultiplier, tileVisibleHeight,  tileTotalWidthOriginal, tileTotalHeightOriginal,\
            tileVisibleHeightOriginal, heightMultiplierTab, screenWidth, xScreenOffset, yScreenOffset
    tileTotalWidth = tileTotalWidthOriginal * scaleMultiplier  # width of tile image, as stored in memory
    tileTotalHeight = tileTotalHeightOriginal * scaleMultiplier # height of tile image, as stored in memory
    tileVisibleHeight = tileVisibleHeightOriginal * scaleMultiplier # height "visible" part of the image, as stored in memory
    heightMultiplierTab = [tileTotalHeight/ x for x in [2.5,4.5,9.9]] # height multiplier respectively for whole block, half block and quarter block (in terms of thickness)
    xScreenOffset = screenWidth/2 - tileTotalWidth/2
    yScreenOffset = 6*tileTotalHeight # border. Could be 0.    
    loadAllImages()
    return

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# spritesheet-specific -- as stored on the disk ==> !!! here, assume 128x111 with 64 pixels upper-surface !!!
# Values will be updated *after* image loading and *before* display starts
tileTotalWidthOriginal = 151  # width of tile image
tileTotalHeightOriginal = 107 # height of tile image
tileVisibleHeightOriginal = 59 # height "visible" part of the image, i.e. top part without subterranean part

###


tileType = []
objectType = []
agentType = []

noObjectId = noAgentId = 0
burningTreeId = 1
ashesId = 2
burningGrassId = 3

predaId   = 1
preyId    = 4
dropperId = 7
playerId  = 8

coinId  = 102

rockId    = 108
snowmanId = 109

imagesShown = [
    loadImage('final_data/player2.png'    ,107,128),
    loadImage('final_data/coinGold_SE.png',54,46),
    loadImage('final_data/ghost.png'      ,107,128),
    loadImage('final_data/ghost_pinky.png',107,128),
    loadImage('final_data/invader_ret.png',107,128),
    loadImage('final_data/invader_ret_hungry.png',107,128),
]
###

# re-scale reference image size -- must be done *after* loading sprites
resetImages()

###

terrainMap    = [x[:] for x in [[0] * worldWidth] * worldHeight] # type of ground tile
heightMap     = [x[:] for x in [[1] * worldWidth] * worldHeight] # height of ground tile
objectMap     = [ [ [ 0 for i in range(worldWidth) ] for j in range(worldHeight) ] for k in range(objectMapLevels) ]
agentMap      = [x[:] for x in [[0] * worldWidth] * worldHeight]
cptTab        = [x[:] for x in [[0] * worldWidth] * worldHeight] # counter for objects
seasonTab     = [x[:] for x in [[0] * worldWidth] * worldHeight] # keep tracks of trees in season

###

# set initial position for display on screen
xScreenOffset = screenWidth/2 - tileTotalWidth/2
yScreenOffset = 3*tileTotalHeight # border. Could be 0.

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def displayWelcomeMessage():

    print ("")
    print ("=-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-=")
    print ("=-=  World of Isotiles                          =-=")
    print ("=-=                                             =-=")
    print ("=-=  nicolas.bredeche(at)sorbonne-universite.fr =-=")
    print ("=-=  licence CC:BY:SA                           =-=")
    print ("=-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-= =-=")
    print (">> v.",versionTag)
    print ("")

    print ("Screen resolution : (",screenWidth,",",screenHeight,")")
    print ("World surface     : (",worldWidth,",",worldHeight,")")
    print ("View surface      : (",viewWidth,",",viewHeight,")")
    print ("Verbose all       :",verbose)
    print ("Verbose fps       :",verboseFps)
    print ("Maximum fps       :",maxFps)
    print ("")

    print ("# Hotkeys:")
    print ("\tcursor keys : move around (use shift for tile-by-tile move)")
    print ("\tv           : verbose mode")
    print ("\tf           : display frames-per-second")
    print ("\to           : decrease view surface")
    print ("\tO           : increase view surface")
    print ("\ts           : decrease scaling")
    print ("\tS           : increase scaling")
    print ("\tESC         : quit")
    print ("")

    return

def getWorldWidth():
    return worldWidth

def getWorldHeight():
    return worldHeight

def getViewWidth():
    return viewWidth

def getViewHeight():
    return viewHeight

def getTerrainAt(x,y):
    return terrainMap[y][x]

def setTerrainAt(x,y,type):
    terrainMap[y][x] = type

def getHeightAt(x,y):
    return heightMap[y][x]

def setHeightAt(x,y,height):
    heightMap[y][x] = height

def getObjectAt(x,y,level=0):
    if level < objectMapLevels:
        return objectMap[level][y][x]
    else:
        print ("[ERROR] getObjectMap(.) -- Cannot return object. Level ",level," does not exist.")
        return 0

def setObjectAt(x,y,type,level=0): # negative values are possible: invisible but tangible objects (ie. no display, collision)
    if level < objectMapLevels:
        objectMap[level][y][x] = type
    else:
        print ("[ERROR] setObjectMap(.) -- Cannot set object. Level ",level," does not exist.")
        return 0

def getAgentAt(x,y):
    return agentMap[y][x]

def setAgentAt(x,y,type):
    agentMap[y][x] = type

def getXScreen(x,y,widthGap=0):
    xScreen = xScreenOffset + x * tileTotalWidth / 2 - y * tileTotalWidth/ 2 + widthGap*scaleMultiplier
    return xScreen

def getYScreen(x,y,height,heightGap=0):
    yScreen = yScreenOffset + y * tileVisibleHeight / 2 + x * tileVisibleHeight / 2 + heightGap*scaleMultiplier - height 
    return yScreen

def getTotalHeightDiff(x,y,level): #height difference of object compared to ground level
    if getObjectAt(x,y,level) != 0:
        diff_height = heightMultiplierTab[objectType[getObjectAt(x,y,level)][3]]
        if level > 0:
            diff_tile = (objectType[ getObjectAt( x, y, level)][2] - objectType[ getObjectAt( x, y, level-1)][2]) * scaleMultiplier
        else:
            diff_tile = (objectType[ getObjectAt( x, y, level)][2] - tileType[ getTerrainAt( x, y)][2]) * scaleMultiplier
    return diff_height - diff_tile

def getTotalWidthDiff2(x,y,level): #help with debugging
    global printed
    if level > 0:
        if getObjectAt(x,y,level - 1) == 0 and printed == False:
            print('x = ',x,' y = ',y,' level = ',level, '\n', heightMap[y][x],'\n',objectMap[level][y][x],'\n',objectMap[level-1][y][x],'\n',terrainMap[y][x])
            printed = True 
            return
        else:           
            diff = objectType[getObjectAt(x,y,level)][1] - objectType[getObjectAt(x,y,level-1)][1]
    else:
        diff = objectType[getObjectAt(x,y,level)][1] - tileType[getTerrainAt(x,y)][1]
    return diff*scaleMultiplier

def getTotalWidthDiff(x,y,level): #width difference of object compared to object or ground right below
    if level > 0:
        diff = objectType[getObjectAt(x,y,level)][1] - objectType[getObjectAt(x,y,level-1)][1]
    else:
        diff = objectType[getObjectAt(x,y,level)][1] - tileType[getTerrainAt(x,y)][1]
    return diff*scaleMultiplier

def getHaltonSeqInd(i): # to generate evenly dispersed tree growing
    f2 = f3 = 1
    r2 = r3 = 0
    i2 = i3 = i
    while i2 > 0:
        f2 = f2 / 2
        r2 = r2 + f2 * (i2 % 2)
        i2 = i2 // 2
    while i3 > 0:
        f3 = f3 / 3
        r3 = r3 + f3 * (i3 % 3)
        i3 = i3 // 3
    return r2,r3

def setSeason(season):
    global flow, addWave
    if season == 4:
        flow = False
        addWave = False
        setObjectAt(40,12,snowmanId,1)
    else:
        flow = True
        addWave = True
        setObjectAt(40,12,rockId,1)

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def render( it = 0 ):
    global xViewOffset, yViewOffset

    pygame.draw.rect(screen, (0,0,0), (0, 0, screenWidth, screenHeight), 0) # overkill - can be optimized. (most sprites are already "naturally" overwritten)

    for y in range(getViewHeight()):
        for x in range(getViewWidth()):
            # assume: north-is-upper-right

            xTile = ( xViewOffset + x + getWorldWidth() ) % getWorldWidth()
            yTile = ( yViewOffset + y + getWorldHeight() ) % getWorldHeight()
            heightMultiplier = tileTotalHeight/4
            heightNoise = 0
            if addWave == True: # add sinusoidal noise on height positions
                heightNoise = math.sin(it/23+yTile) * math.sin(it/7+xTile) * heightMultiplier/10 + math.cos(it/17+yTile+xTile) * math.cos(it/31+yTile) * heightMultiplier
                heightNoise = math.sin(it/199) * heightNoise

            height = getHeightAt( xTile , yTile ) * heightMultiplierTab[tileType[terrainMap[yTile][xTile]][3]]

            xScreen = getXScreen(x,y,tileType[terrainMap[yTile][xTile]][1])
            yScreen = getYScreen(x,y,height,tileType[terrainMap[yTile][xTile]][2])

            screen.blit( tileType[ getTerrainAt( xTile , yTile ) ][0] , (xScreen, yScreen)) # display terrain

            for level in range(objectMapLevels):                
                if getObjectAt( xTile , yTile , level)  > 0: # object on terrain?
                    xScreen = xScreen + getTotalWidthDiff2(xTile, yTile, level)
                    yScreen = yScreen - getTotalHeightDiff(xTile, yTile,level) 
                    if getObjectAt( xTile , yTile , level) in (61,60): #water?
                    	screen.blit( objectType[ getObjectAt( xTile , yTile, level) ][0] , (xScreen,yScreen - heightNoise)) 
                    else:
                    	screen.blit( objectType[ getObjectAt( xTile , yTile, level) ][0] , (xScreen,yScreen)) 

            if getAgentAt( xTile, yTile ) != 0: # agent on terrain?
                screen.blit( agentType[ getAgentAt( xTile, yTile ) ][0] , (xScreen, yScreen - heightMultiplierTab[0] ))

    return

class BasicAgent:

    def __init__(self,imageId,x = randint(0,getWorldWidth()-1),y = randint(0,getWorldWidth()-1)):
        self.type = imageId
        self.x = x
        self.y = y
        self.cpt = 0
        self.reset()
        return

    def reset(self):
        if self.type == preyId or self.type == predaId:
            while not (getTerrainAt(self.x,self.y) in (3,6,8,5))\
            or getObjectAt(self.x,self.y) != 0 or getAgentAt(self.x,self.y) != 0:
                self.x = randint(0,getWorldWidth()-1)
                self.y = randint(0,getWorldHeight()-1)
            setAgentAt(self.x,self.y,self.type)
        elif self.type == dropperId:#  or self.type == playerId:
            while getTerrainAt(self.x,self.y) != 6 or getObjectAt(self.x,self.y) != 0 \
                 or getAgentAt(self.x,self.y) != 0 or getHeightAt(self.x,self.y) != 1:
                self.x = randint(0,getWorldWidth()-1)
                self.y = randint(0,getWorldHeight()-1)
            setAgentAt(self.x,self.y,self.type)       
        elif self.type == playerId:
            setAgentAt(self.x,self.y,self.type)     
        return

    def getPosition(self):
        return (self.x,self.y)

    def movePrey(self): #move to food in neighborhood, move randomly in case no food found, eat food to survive
        success = False
        xNew = self.x
        yNew = self.y
        self.cpt += 1
        neighbours = ((+1,0),(0,+1),(-1,0),(0,-1)) #list((x,y)) #SE,SW,NE,NW
        edible_neighbours = [0]*4
        for i in range(4):
            if getObjectAt((self.x+neighbours[i][0])%getWorldWidth(),(self.y+neighbours[i][1])%getWorldHeight()) >= 21\
            and getObjectAt((self.x+neighbours[i][0])%getWorldWidth(),(self.y+neighbours[i][1])%getWorldHeight()) < 27:
                edible_neighbours[i] = 1
        i = 0
        while i<4 and edible_neighbours[i] == 0: #first edible food encountered clockwise
            i+=1
        if i == 4: #no food in neighborhood           
            if random() < 0.5:
                xNew = ( self.x + [-1,+1][randint(0,1)] + getWorldWidth() ) % getWorldWidth()
            else:
                yNew = ( self.y + [-1,+1][randint(0,1)] + getWorldHeight() ) % getWorldHeight() 
        else:
            xNew = (self.x+neighbours[i][0])%getWorldWidth()
            yNew = (self.y+neighbours[i][1])%getWorldHeight()
        
        #get highest object existant
        level = 0
        while level < objectMapLevels and getObjectAt( xNew , yNew, level) != 0:
            level += 1
        level -= 1
        cur_ob = getObjectAt(xNew,yNew,level) 
        if cur_ob in (33,0) or (cur_ob >= 36 and cur_ob < 40) or (cur_ob >= 44 and cur_ob < 48) \
        or (cur_ob >= 98 and cur_ob < 102) or (cur_ob >= 21 and cur_ob < 27) or (cur_ob in (60,61) and season == 4):
        #tile contains no object or mountain surface or ice on mountain or edges or stairs or coins
            success = True

        if getObjectAt(xNew,yNew) in (60,61):
        #water can only be walked on in winter
            if season == 4 and level < 2:
                success = True
            else:
                if cur_ob >= 98 and cur_ob < 102:
                #stairs can be walked on anytime
                    success = True
                else:
                    success = False

        if getAgentAt(xNew,yNew) != 0:
            success = False
        #preys can walk on mountains, stairs, edges, ice and eat grass
        if success:

            if getObjectAt(xNew,yNew) >= 21 and getObjectAt(xNew,yNew) < 27:
                if verbose == True:
                    print("prey ate after ",self.cpt)
                    print("food found x = ", xNew," y = ",yNew," type = ",getObjectAt(xNew,yNew))
                self.type = preyId + 1
                self.cpt = 0
                setObjectAt(xNew,yNew,0) #food eaten
            if getAgentAt(self.x,self.y) not in (predaId, predaId + 1, predaId + 2): #prey caught at self.x,self.y escapes to xNew,yNew
                setAgentAt(self.x,self.y,noAgentId)
            else:
                if verbose == True:
                    print("prey caught at x = ",self.x," y = ",self.y," ESCAPED to x = ",xNew," y = ",yNew)                
            self.x = xNew
            self.y = yNew
            setAgentAt(self.x,self.y,self.type)
        if verbose == True:
            print ("agent of type ",str(self.type),"located at (",self.x,",",self.y,")")        
        return

    def movePreda(self): #move to catch prey in neighborhood, move randomly in case no prey found, eat prey to survive
        success = False
        xNew = self.x
        yNew = self.y   
        x_prey_caught = -1
        y_prey_caught = -1
        self.cpt += 1     
        neighbours = ((+1,0),(0,+1),(-1,0),(0,-1)) #list((x,y)) #SE,SW,NE,NW
        edible_neighbours = [0]*4
        for i in range(4): 
            if getAgentAt((self.x+neighbours[i][0])%getWorldWidth(),(self.y+neighbours[i][1])%getWorldHeight()) in (preyId, preyId + 1, preyId + 2):
                edible_neighbours[i] = 1
        i = 0
        while i<4 and edible_neighbours[i] == 0: #first prey encountered clockwise
            i = i + 1
        if i == 4: #no prey in neighborhood            
            if random() < 0.5:
                xNew = ( self.x + [-1,+1][randint(0,1)] + getWorldWidth() ) % getWorldWidth()
            else:
                yNew = ( self.y + [-1,+1][randint(0,1)] + getWorldHeight() ) % getWorldHeight() 
        else:
            xNew = (self.x+neighbours[i][0])%getWorldWidth()
            yNew = (self.y+neighbours[i][1])%getWorldHeight()

        #get highest object existant
        level = 0
        while level < objectMapLevels and getObjectAt( xNew , yNew, level) != 0:
            level += 1
        level -= 1
        cur_ob = getObjectAt(xNew,yNew,level) 
        if cur_ob in (33,0) or (cur_ob >= 36 and cur_ob < 40) or (cur_ob >= 44 and cur_ob < 48) \
        or (cur_ob >= 98 and cur_ob < 102) or (cur_ob in (60,61) and season == 4):
        #tile contains no object or mountain surface or ice on mountain or edges or stairs or coins
            success = True

        if getObjectAt(xNew,yNew) in (60,61):
        #water can only be walked on in winter
            if season == 4 and level < 2:
                success = True
            else:
                if cur_ob >= 98 and cur_ob < 102:
                #stairs can be walked on anytime
                    success = True
                else:
                    success = False

        if getAgentAt(xNew,yNew) not in (0,preyId,preyId + 1,preyId + 2,playerId):
            success = False
        #predators can walk on mountains, stairs, edges, ice and eat preys
        if success:        
            if getAgentAt(xNew,yNew) in (preyId, preyId + 1, preyId + 2): #a prey found
                if verbose == True:
                    print("prey found x = ", xNew," y = ",yNew," cpt = ",self.cpt)
                x_prey_caught = xNew
                y_prey_caught = yNew
            setAgentAt(self.x,self.y,noAgentId)
            self.x = xNew
            self.y = yNew
            setAgentAt(self.x,self.y,self.type)
        if verbose == True:
            print ("agent of type ",str(self.type),"located at (",self.x,",",self.y,")")   
        return x_prey_caught,y_prey_caught

    def movePlayer(self,xNew,yNew):
        global nbCoin
        success = False
        #get highest object existant
        level = 0
        while level < objectMapLevels and getObjectAt( (self.x+xNew+worldWidth)%worldWidth , (self.y+yNew+worldHeight)%worldHeight , level) != 0:
            level += 1
        level -= 1
        xNew = (self.x+xNew+worldWidth)%worldWidth
        yNew = (self.y+yNew+worldHeight)%worldHeight

        cur_ob = getObjectAt(xNew, yNew, level)

        if cur_ob in (33,0) or (cur_ob >= 36 and cur_ob < 40) or (cur_ob >= 44 and cur_ob < 48) \
        or (cur_ob >= coinId and cur_ob < coinId + 4) or (cur_ob >= 98 and cur_ob < 102) \
        or (cur_ob in (60,61) and season == 4):
        #tile contains no object or mountain surface or ice on mountain or edges or stairs or coins
            success = True

        if getObjectAt(xNew,yNew) in (60,61):
        #water can only be walked on in winter
            if season == 4 and level < 2:
                success = True
            else:
                if cur_ob >= 98 and cur_ob < 102:
                #stairs can be walked on anytime
                    success = True
                else:
                    success = False

        if getAgentAt(xNew,yNew) in (dropperId,preyId,preyId + 1,preyId + 2):
            success = False
        #player can walk on mountains, stairs, edges, ice and collect coins

        if success:
            setAgentAt( self.x, self.y, noAgentId)
            self.x = xNew
            self.y = yNew
            setAgentAt( self.x, self.y, self.type)
            if (cur_ob >= coinId and cur_ob < coinId + 4):
                nbCoin += 1
                setObjectAt(self.x,self.y,0,level)  
        if verbose == True:
            if success == False:
                print ("agent of type ",str(self.type)," cannot move.")
            else:
                print ("agent of type ",str(self.type)," moved to (",self.x,",",self.y,")")
        return

    def getType(self):
        return self.type

class Dropper(BasicAgent):
    def __init__(self,imageId,x = randint(0,getWorldWidth()-1),y = randint(0,getWorldWidth()-1),orient = 0,d = 1):
        super().__init__(imageId,x,y)
        self.orient = orient 
        self.d = d # d = 1 clockwise direction, d = -1 counterclockwise
        return

    def moveDropper(self): 
        #move straight in 1 direction until encounter obstacle, find new direction clockwise
        #change to anticlockwise if no new direction works and vice versa, repeat until new direction found or dead
        #move to survive
        self.cpt +=1
        neighbours = ((+1,0),(0,+1),(-1,0),(0,-1)) #list((x,y)) #SE,SW,NE,NW

        if random() < 0.3: # random change of orientation to avoid stucking in the same path
            self.orient +=1
            if verbose == True:
                print ("orient changed to ",self.orient)
        self.orient = (self.orient + 4) % 4
        if verbose == True:
            print ("orient = ",self.orient," x = ",self.x," y = ",self.y, " d = ", self.d)

        xNew = (self.x + neighbours[self.orient][0] + getWorldWidth()) % getWorldWidth()
        yNew = (self.y + neighbours[self.orient][1] + getWorldHeight()) % getWorldHeight()

        while self.orient < 4 and self.orient >= 0 and not(getAgentAt(xNew,yNew) == 0 and (getObjectAt(xNew,yNew) == 0 \
        or (getObjectAt(xNew,yNew) >= coinId and getObjectAt(xNew,yNew) < coinId+4)\
        or (getObjectAt(xNew,yNew) >= 36 and getObjectAt(xNew,yNew) < 40)\
        or (getObjectAt(xNew,yNew) >= 44 and getObjectAt(xNew,yNew) < 48)\
        or (season == 4 and getObjectAt(xNew,yNew) in (61,60) and getObjectAt(xNew,yNew,2) == 0))):
        #dropper can walk on edges and coins and water (ice) in winter
            if verbose == True:
                print("orient = ",self.orient," obstacle = ",getObjectAt(xNew,yNew))   
            self.orient += self.d 
            if self.orient == 4 or self.orient == -1:
                continue                    
            xNew = (self.x + neighbours[self.orient][0] + getWorldWidth()) % getWorldWidth()
            yNew = (self.y + neighbours[self.orient][1] + getWorldHeight()) % getWorldHeight()             

        if self.orient < 4 and self.orient >= 0: #dropper can move
            self.cpt = 0
            setAgentAt(self.x,self.y,noAgentId)
            if getObjectAt(self.x,self.y) == 0 \
            or (getObjectAt(self.x,self.y) >= coinId and getObjectAt(self.x,self.y) < coinId+4):
                setObjectAt(self.x,self.y,coinId + self.orient)
            elif getObjectAt(self.x,self.y,1) != 0 and (getObjectAt(self.x,self.y,1) < coinId or getObjectAt(self.x,self.y,1) >= coinId + 4):
            #cliff on water
                setObjectAt(self.x,self.y,coinId + self.orient,2)                
                if verbose == True:
                    print("debug x = ",xNew," y = ",yNew," object = ",getObjectAt(xNew,yNew))
            else:
            #cliff in land
                setObjectAt(self.x,self.y,coinId + self.orient,1)
            self.x = xNew
            self.y = yNew
            setAgentAt(self.x,self.y,self.type)
        else:
            if verbose == True:
                print("didnt move, change direction")
            self.orient -= self.d
            self.d = -self.d

        if verbose == True:
            print ("agent of type ",str(self.type),"located at (",self.x,",",self.y,")")
        return

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

def initWorld():
    global nbTrees, nbBurningTrees, nbPineTrees, nbHerbs

    MountainsTerrainMap = [ 
    [1,1,1,1,1,  1,1,1,1,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  0,0,1,1,1,   1,1,1,1,1,  1,1,1,1,1,  1,0,0,0,0,  0,1,1,1,1,   1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,0,0,  0,1,1,1,1,   1,1,1,1,1,  1,1,1,1,0,  0,0,0,0,0,  1,1,1,1,1,   1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,0,0,1,  1,1,1,1,1,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,1,1,1,   1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,0,0,  1,1,1,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,1,   1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
 
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  1,1,1,1,1,  1,1,1,1,1],
    [0,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0],
    [0,0,1,1,1,  1,1,1,1,1,  1,1,1,1,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0],
    [0,0,1,1,0,  0,0,0,0,1,  1,1,1,1,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0],
    ]

    x_offset = 0
    y_offset = 0
    for y in range( len( MountainsTerrainMap ) ):
        for x in range( len( MountainsTerrainMap[0] ) ):
            setTerrainAt( x+x_offset, y+y_offset, MountainsTerrainMap[y][x]) 
            if MountainsTerrainMap[y][x] == 1:
                setHeightAt( x+x_offset, y+y_offset, 2+getHeightAt(x+x_offset, y+y_offset))

    ############
    MainForestTerrainMap = [[6]*30]*40
    x_offset = 30
    y_offset = 18

    for y in range( len( MainForestTerrainMap ) ):
        for x in range( len(MainForestTerrainMap[0] ) ):
            setTerrainAt( x+x_offset, y+y_offset, MainForestTerrainMap[y][x] )

    SmallNorthWaterMap = [
    [0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,1],
    [0,0,0,0,0,  0,1,1,1,0,  0,0,1,1,1],
    [0,0,0,0,1,  1,1,1,0,0,  0,1,1,1,1],
    [0,0,1,1,1,  1,1,1,1,1,  0,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
    ]
    x_offset = 40
    y_offset = 13
    for y in range( len( SmallNorthWaterMap ) ):
        for x in range( len(SmallNorthWaterMap[0] ) ):
            if SmallNorthWaterMap[y][x] == 1:
                setTerrainAt( x+x_offset, y+y_offset, 6) 
                setHeightAt( x+x_offset, y+y_offset, 2 + getHeightAt( x+x_offset, y+y_offset))
            else:
                setTerrainAt( x+x_offset, y+y_offset, 0 )


    BigSouthWaterMap = [
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,0,0,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,0,0,1,  1,1,1,1,0,  0,0,0,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,0,0,  0,1,1,1,0,  0,0,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,0,0,0,  0,0,0,0,0,  0,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,1,1,  1,1,1,1,1],  
    ]
    x_offset = 30
    y_offset = 52
    for y in range( len( BigSouthWaterMap ) ):
        for x in range( len(BigSouthWaterMap[0] ) ):
            if BigSouthWaterMap[y][x] == 1:
                setTerrainAt( x+x_offset, y+y_offset, 6)
            else:
                setTerrainAt( x+x_offset, y+y_offset, 0)

    ############
    LeftTerrainMap = [
    [1,1,1,1,1,  1,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,1],
    [1,1,1,1,1,  1,1,1,0,0,  0,0,1,1,1,  1,1,1,1,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  0,0,0,0,0,   0,0,0,0,0,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,0,0,0,   0,0,0,0,1,  1,1,1,1,1],

    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,0,   0,0,0,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,   0,0,0,0,0,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,0,   0,0,0,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,0,   0,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,0,0,   1,1,1,1,1,  1,1,1,1,1],

    [1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,1,  1,1,1,1,0,  0,0,0,0,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,1,1,1,  1,1,1,1,1,  1,1,0,0,0,  0,0,0,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,1,  1,1,1,1,1,  1,1,1,0,0,  0,0,0,0,0,   1,1,1,1,1,  1,1,1,1,1],
    [1,3,3,3,3,  3,3,3,3,3,  3,1,1,1,1,  1,1,1,1,1,  1,1,0,0,0,   0,1,1,1,1,  1,1,1,1,1],
    [1,3,3,3,3,  3,3,3,3,3,  3,3,3,3,1,  1,1,1,1,1,  1,1,1,0,0,   0,0,0,0,1,  1,1,1,1,1],

    [1,1,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  1,1,1,1,0,   0,0,0,0,0,  1,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,0,   0,0,0,0,0,  0,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,0,   0,0,0,0,0,  0,0,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,0,0,0,0,   0,0,0,0,0,  0,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  0,0,0,0,0,   0,0,0,0,1,  1,1,1,1,1],

    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  0,0,0,0,0,   0,0,0,0,0,  1,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,0,0,  0,0,0,0,0,   0,0,0,0,1,  1,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,0,0,0,0,  0,0,0,0,0,   0,0,0,1,1,  1,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,0,0,0,  0,0,0,0,0,   0,0,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,0,0,  0,0,0,0,0,   0,0,0,1,1,  1,1,1,1,1],

    [1,1,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,0,0,0,  0,0,0,0,0,   0,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,0,0,0,0,  0,0,0,0,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,0,  0,0,0,0,0,  0,1,1,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  0,0,0,1,1,  1,1,1,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  0,0,0,1,1,  1,1,1,1,1,   1,1,1,1,1,  1,1,1,1,1],

    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,0,0,1,  1,1,1,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,0,0,  0,1,1,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  0,0,0,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,0,0,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,0,0,0,1,   1,1,1,1,1,  1,1,1,1,1],

    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,0,  0,0,0,1,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,0,0,1,   1,1,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  0,0,0,0,0,   0,0,1,1,1,  1,1,1,1,1],
    [1,1,1,1,3,  3,3,3,3,3,  3,3,3,3,3,  3,3,0,0,0,  0,0,0,0,0,   0,0,0,0,1,  1,1,1,1,1],
    [1,1,3,3,3,  3,3,3,3,3,  3,3,3,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,1,1,1,1],

    [0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,   0,0,0,0,0,  0,0,0,0,0]
    ]
    x_offset = 55
    y_offset = 19
    for y in range( len( LeftTerrainMap ) ):
        for x in range( len(LeftTerrainMap[0] ) ):
            if LeftTerrainMap[y][x] == 1:
                setTerrainAt((x+x_offset)%worldWidth, y+y_offset, 6) #normal ground
            else:
                setTerrainAt( (x+x_offset)%worldWidth, y+y_offset, LeftTerrainMap[y][x]) #others

    #### main forest ####
    for y in range(18,getWorldHeight()-1):
        for x in range(12,getWorldWidth()-1):
            if (terrainMap[y][x-1] == 0 or getHeightAt(x-1,y) == 3) and terrainMap[y][x] == 6:
                setHeightAt(x,y,2+getHeightAt(x,y))

    #### main forest higher part ####
    for y in range(26,50):
        for x in range(30,55):
            setHeightAt(x,y,5)

    for y in range(21,29):
        for x in range(39,57):
            setHeightAt(x,y,5)


    PineForestHeightMap = [
    [0,2,3,4,4,  5,0,0,0,0,  0,0,0,0,0,  0,0,0,0,0,  5,4,4,3,2,  1],
    [1,2,2,3,4,  5,5,0,0,0,  0,0,0,0,0,  0,0,0,0,5,  4,4,3,2,2,  1],
    [1,1,2,3,4,  4,5,0,0,5,  5,5,5,5,0,  0,0,0,0,4,  3,3,2,2,1,  0],
    
    [0,1,1,2,3,  4,4,5,5,5,  4,4,4,5,5,  5,5,5,5,4,  3,2,2,1,1,  0],
    [0,1,1,2,3,  3,4,4,4,4,  4,3,3,4,4,  4,4,4,4,3,  3,2,2,1,1,  0],
    [0,0,1,2,2,  3,3,3,3,3,  3,3,3,3,3,  3,3,3,3,3,  2,2,1,1,0,  0],
    [0,0,1,1,2,  2,2,2,2,2,  2,2,2,2,2,  2,2,2,2,2,  1,1,1,0,0,  0],
    [0,0,0,0,1,  1,1,2,2,2,  2,2,2,2,1,  1,1,1,1,1,  1,0,0,0,0,  0],
    
    [0,0,0,0,1,  1,1,1,1,1,  2,2,2,1,1,  0,0,1,1,1,  0,0,0,0,0,  0],
    [0,0,0,0,0,  0,0,1,1,1,  1,1,1,1,0,  0,0,0,0,0,  0,0,0,0,0,  0]
    ]
    x_offset = 55
    y_offset = 8
    for y in range( len( PineForestHeightMap ) ):
        for x in range( len(PineForestHeightMap[0] ) ):
            setHeightAt( (x+x_offset)%worldWidth, y+y_offset, PineForestHeightMap[y][x] + getHeightAt((x+x_offset)%worldWidth,y+y_offset))
            if PineForestHeightMap[y][x] != 0:
                setTerrainAt( (x+x_offset)%worldWidth, y+y_offset, 7)

    #### set water base ####
    for y in range(worldHeight):
        for x in range(worldWidth):
            if terrainMap[y][x] == 0:
                setObjectAt(x,y,61,0)

    neighbours = ((+1,0),(0,+1),(-1,0),(0,-1)) #list((x,y)) #SE,SW,NE,NW

    #### set common base for mountains ####
    x_offset = 0
    y_offset = 0
    for y in range( len( MountainsTerrainMap ) ):
        for x in range( len( MountainsTerrainMap[0] ) ):
            if getTerrainAt(x+x_offset,y+y_offset) == 1:
                not_mountain_neighbours = [0]*4
                for i in range(4):
                    if getTerrainAt((x+x_offset+neighbours[i][0]+getWorldWidth())%getWorldWidth(),(y+y_offset+neighbours[i][1]+getWorldHeight())%getWorldHeight()) == 7\
                    and getHeightAt((x+x_offset+neighbours[i][0]+getWorldWidth())%getWorldWidth(),(y+y_offset+neighbours[i][1]+getWorldHeight())%getWorldHeight()) != 1:
                        not_mountain_neighbours[i] = 1                       
                if not_mountain_neighbours[1] == 0:
                    setObjectAt( x+x_offset, y+y_offset, 33)
                    setObjectAt( x+x_offset, y+y_offset, 33, 1)
                else:
                    if not_mountain_neighbours[1] == 1:
                        setObjectAt(x+x_offset,y+y_offset, 56+1)
                        setObjectAt(x+x_offset,y+y_offset, 48+1, 1)                     
    for y in range(9,15):
        for x in range(0,8):
            if getObjectAt(x,y) == 0:
                setObjectAt(x,y,coinId)

    MountHeightMap = [
    [7,7,7,7,7,  4,4,0,0,0],
    [7,7,7,3,3,  3,3,3,0,0],
    [7,7,3,3,3,  3,3,3,3,0],
    [4,3,3,3,3,  3,3,3,3,0],
    [3,3,3,3,3,  3,3,2,2,1],
    [0,3,3,3,3,  2,2,2,2,1],
    [0,0,0,0,0,  0,0,0,1,1],
    ]
    x_offset = 1
    y_offset = 2
    for y in range(len(MountHeightMap)):
        for x in range(len(MountHeightMap[0])):
            if MountHeightMap[y][x] > 0:
                for level in range(2,MountHeightMap[y][x]+2):
                    setObjectAt( x+x_offset, y+y_offset, 33, level)
 
    #### set edges for main forest ####
    for y in range(13,getWorldHeight()-1):
        for x in range(12,getWorldWidth()-1):
            if terrainMap[y][x] == 6:
                for i in range(4) :
                    if getHeightAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight) < getHeightAt(x,y):
                        level = 0
                        while getObjectAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight,level) in (61,60): # tile with water
                            level = level + 1
                        setObjectAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight,44+i,level)

    # fix edges and set corners for main forest # 
    for y in range(13,getWorldHeight()-1):
        for x in range(12,getWorldWidth()-1):
            higher_neighbours = [0]*4
            for i in range(4):
                if getTerrainAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight) == 6 \
                and getHeightAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight) > getHeightAt(x,y):
                    higher_neighbours[i] = 1
            level = 0
            while getObjectAt(x,y,level) in (60,61) or getObjectAt(x,y,level) == 33: # tile with water
                level = level + 1    
            if higher_neighbours[1] == 1 and higher_neighbours[3] == 1:
                setObjectAt(x,y,45,level) #prefer normal cliff SW over NW
            if higher_neighbours[0] == 1 and higher_neighbours[2] == 1:
                setObjectAt(x,y,44,level) #prefer normal cliff SE over NE
            for i in (0,1,-1,-2): # corner NE,NW,SW,SE
                if higher_neighbours[i] == 1 and higher_neighbours[i+1] == 1:
                    setObjectAt(x,y,38+i,level)

    #### set edges for mountains ####
    for y in range(0,15):
        for x in range(0,getWorldWidth()):
            if terrainMap[y][x] == 1 and getHeightAt(x,y) == 3:
                for i in range(4):
                    if getTerrainAt((x+neighbours[i][0]+worldWidth+worldWidth)%worldWidth, (y+neighbours[i][1]+worldHeight)%worldHeight) != 1 \
                    and getHeightAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight) < 3:
                        level = 0
                        while getObjectAt((x+neighbours[i][0]+worldWidth)%worldWidth, (y+neighbours[i][1]+worldHeight)%worldHeight,level) in (60,61):
                            level = level + 1
                        setObjectAt((x+neighbours[i][0]+worldWidth)%worldWidth, (y+neighbours[i][1]+worldHeight)%worldHeight, 56+i, level)
                        setObjectAt((x+neighbours[i][0]+worldWidth)%worldWidth, (y+neighbours[i][1]+worldHeight)%worldHeight, 56+i, level+1)
                        setObjectAt((x+neighbours[i][0]+worldWidth)%worldWidth, (y+neighbours[i][1]+worldHeight)%worldHeight, 48+i, level+2)                        

    # fix edges and set corners for mountains # 
    for y in range(0,15):
        for x in range(0,getWorldWidth()):
            not_mountain_neighbours = [0]*4
            for i in range(4):
                if getTerrainAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight) == 1 \
                and getHeightAt((x+neighbours[i][0]+worldWidth)%worldWidth,(y+neighbours[i][1]+worldHeight)%worldHeight) > getHeightAt(x,y):
                    not_mountain_neighbours[i] = 1
            level = 0
            while getObjectAt(x,y, level) in (60,61): # tile with water
                level = level + 1    
            if not_mountain_neighbours[1] == 1 and not_mountain_neighbours[3] == 1:
                setObjectAt(x,y,57,level) #prefer normal cliff SW over NW
                setObjectAt(x,y,57,level+1)
                setObjectAt(x,y,49,level+2)
            if not_mountain_neighbours[0] == 1 and not_mountain_neighbours[2] == 1:
                setObjectAt(x,y,56,level) #prefer normal cliff SE over NE
                setObjectAt(x,y,56,level+1)
                setObjectAt(x,y,48,level+2)
            for i in (0,1,-1,-2): # corner NE,NW,SW,SE
                if not_mountain_neighbours[i] == 1 and not_mountain_neighbours[i+1] == 1 and not_mountain_neighbours[i+2] != 1:
                    setObjectAt(x,y,54+i,level)
                    setObjectAt(x,y,54+i,level+1)
                    setObjectAt(x,y,42+i,level+2)
            # neighbours = ((+1,0),(0,+1),(-1,0),(0,-1)) #list((x,y)) #SE,SW,NE,NW

    #### set edges for tall mount ####
    x_offset = 1
    y_offset = 2
    for level in range(2,objectMapLevels):
        for y in range(len(MountHeightMap)):
            for x in range(len(MountHeightMap[0])):
                if getObjectAt(x+x_offset,y+y_offset,level) == 33:
                    for i in range(4):
                        if getObjectAt(x+x_offset+neighbours[i][0],y+y_offset+neighbours[i][1],level) == 0:
                            if level < objectMapLevels-1 and getObjectAt(x+x_offset,y+y_offset,level+1) == 0:
                                setObjectAt(x+x_offset+neighbours[i][0],y+y_offset+neighbours[i][1],48+i,level) #top
                            else:
                                setObjectAt(x+x_offset+neighbours[i][0],y+y_offset+neighbours[i][1],56+i,level) #mid

    # set waterfall on mountain #
    setObjectAt(3,4,67,8) #top
    setObjectAt(3,4,71,7) #mid
    setObjectAt(3,4,71,6)
    setObjectAt(3,4,71,5)

    # set lake on mountain #
    LakeOnMountainMap = [
    [87 ,88 ,0  ,0  ,0  ,0  ,0  ,0  ,0  ],
    [95 ,98 ,109,73 ,73 ,73 ,73 ,88 ,0  ],
    [86 ,89 ,73 ,73 ,73 ,73 ,73 ,97 ,119],
    [0  ,92 ,73 ,73 ,73 ,91 ,94 ,89 ,118],
    [0  ,95 ,73 ,73 ,91 ,89 ,119,0  ,0  ],
    [0  ,86 ,94 ,94 ,89 ,0  ,0  ,0  ,0  ],
    ]
    for y in range(len(LakeOnMountainMap)):
        for x in range(len(LakeOnMountainMap[0])):
            if LakeOnMountainMap[y][x] != 0:
                level = 0
                while getObjectAt(x+x_offset,y+y_offset,level) == 33: #highest not edge level 
                    level = level + 1
                edge_level = 0
                if getObjectAt(x+x_offset,y+y_offset,level + edge_level) != 0:
                    while getObjectAt(x+x_offset,y+y_offset,level + edge_level) != 0:
                        edge_level = edge_level + 1
                    i = 0
                    while i <= edge_level: #set edges to 2 levels higher to make place for added tiles
                        setObjectAt(x+x_offset,y+y_offset,getObjectAt(x+x_offset,y+y_offset,level+edge_level-i),level+edge_level-i+2)
                        i = i + 1
                level = level - 1
                #replace a ground tile of full thickness with 1 ground tile of 1/2 thickness + 1 ground tile of 1/4 thickness + 1 water tile of 1/4 thickness
                #an empty object between 2 layers of non-empty objects not allowed 
                setObjectAt(x+x_offset,y+y_offset,32,level)
                setObjectAt(x+x_offset,y+y_offset,34,level+1)                    
                setObjectAt(x+x_offset,y+y_offset,LakeOnMountainMap[y][x]-12,level+2)

    # set stairs #
    setObjectAt(9,8,99,3)
    setObjectAt(11,8,98,2)

    setObjectAt(40,5,99,1)
    setObjectAt(40,5,0,2)    
    setObjectAt(40,5,0,3)

    setObjectAt(40,4,0,1)
    setObjectAt(40,4,99,0)

    setObjectAt(40,3,99,1)

    # set bonus coins #
    for y in range(len(MountainsTerrainMap)):
        for x in range(35,58):
            if getObjectAt(x,y,1) == 33:
                setObjectAt(x,y,coinId,2)

    # remove water to make space for water coming down from the lake on mountain #
    for y in range(16,30):
        for x in range(-3,24):
            if getObjectAt(x,y) == 61 and getObjectAt(x,y,1) == 0:
                setObjectAt(x,y,0)

    for y in range(8,16):
        for x in range(5,23):
            if getObjectAt(x,y) == 61 and getObjectAt(x,y,1) == 0:
                setObjectAt(x,y,0)

    # decoration #
    #setObjectAt(11,48,bridgeId)
    #setObjectAt(40,12,snowmanId,1)
    setObjectAt(40,12,rockId,1)

    #### calculate appropriate amount of trees compared to entire tree growing surface ####
    nbTrees = 0
    for y in range(getWorldHeight()):
        for x in range(getWorldWidth()):
            if getTerrainAt(x,y) == 6 or getTerrainAt(x,y) == 3:
                nbTrees = nbTrees + 1
    nbTrees = int(nbTrees * 0.15)
    nbHerbs = int(nbTrees * 0.05)

    #### trees for pine trees forest ####
    for i in range(nbPineTrees):
        x = randint(0,getWorldWidth()-1)
        y = randint(0,20)
        while getTerrainAt(x,y) != 7 or getObjectAt(x,y) != 0: #only ground type 7 can grow pine tree
            x = randint(0,getWorldWidth()-1)
            y = randint(0,20)
        setObjectAt(x,y,randrange(16,21))
        seasonTab[y][x] = season

    setObjectAt(14,9,19) #stop player from going down this way

    #### trees and herbs for main forest ####
    cpt = 0
    i = 0
    while cpt < nbHerbs * 3/4:
        x,y = getHaltonSeqInd(i)
        x = int(getWorldWidth()*x)
        y = int(getWorldHeight()*y)
        while getObjectAt(x,y) != 0 or (getTerrainAt(x,y) != 3 and getTerrainAt(x,y) != 6) :
            i = i + 1
            x,y = getHaltonSeqInd(i)
            x = int(getWorldWidth()*x)
            y = int(getWorldHeight()*y)
        setObjectAt(x,y,choice([22,23,24,25,26]))
        cpt = cpt + 1

    while cpt < nbHerbs:
        x = randint(0,getWorldWidth()-1)
        y = randint(0,getWorldHeight()-1)
        while getObjectAt(x,y) != 0 or getTerrainAt(x,y) != 3 :
            x = randint(0,getWorldWidth()-1)
            y = randint(0,getWorldHeight()-1)
        setObjectAt(x,y,choice([22,23,24,25,26]))
        cpt = cpt + 1

    cpt = 0
    i = i + 1
    while cpt < nbTrees * 3/4:
        x,y = getHaltonSeqInd(i)
        x = int(getWorldWidth()*x)
        y = int(getWorldHeight()*y)
        while getObjectAt(x,y) != 0 or getTerrainAt(x,y) != 6 :
            i = i + 1
            x,y = getHaltonSeqInd(i)
            x = int(getWorldWidth()*x)
            y = int(getWorldHeight()*y)
        setObjectAt(x,y,choice([4,7,10,13]))
        seasonTab[y][x] = season
        cpt = cpt + 1

    while cpt < nbTrees:
        x = randint(0,getWorldWidth()-1)
        y = randint(0,getWorldHeight()-1)
        while getObjectAt(x,y) != 0 or getTerrainAt(x,y) != 6 :
            x = randint(0,getWorldWidth()-1)
            y = randint(0,getWorldHeight()-1)
        setObjectAt(x,y,choice([4,7,10,13]))
        seasonTab[y][x] = season
        cpt = cpt + 1
    #setObjectAt(5,25,0) # make place for player

    return

### ### ### ### ###

def initAgents():
    for i in range(nbPrey):
        agents.append(BasicAgent(preyId))
    for i in range(nbPreda):
        agents.append(BasicAgent(predaId))
    return

### ### ### ### ###

def stepWorld( it = 0 ):
    global flow_height,drops,water_on_mount
    if it % (maxFps/10) == 0:
#        print("flow height ",flow_height)
        if flow_height < 7 and flow_height  > 0 and it % 10 == 0 :
            flow_height -= 1
        drops = 15
        for y in range(worldHeight):
            for x in range(worldWidth):

                #ground to snowed ground
                if getTerrainAt(x,y) == 3:
                    if season == 4 and random() < 0.2:
                        setTerrainAt(x,y,5)
                if getTerrainAt(x,y) == 6:
                    if season == 4 and random() < 0.2:
                        setTerrainAt(x,y,8)

                #snowed ground back to normal ground
                if getTerrainAt(x,y) == 5:
                    if season != 4 and random() < 0.2:
                        setTerrainAt(x,y,3)
                if getTerrainAt(x,y) == 8:
                    if season != 4 and random() < 0.2:
                        setTerrainAt(x,y,6)

                #tree and herb regrow
                if getTerrainAt(x,y) in (3,6) and getObjectAt(x,y) == 0 and getAgentAt(x,y) == 0: 
                    r = random()
                    if r < probaTreeGrow[season - 1]:
                        setObjectAt(x,y,choice([4,7,10,13]) + season - 1)
                        seasonTab[y][x] = season
                    elif r < probaGrassGrow[season - 1]:
                        setObjectAt(x,y,choice([21,22,23,24,25,26])) 

                #normal trees
                if getObjectAt(x,y) >= 4 and getObjectAt(x,y) < 16:
                    if season != last_season and last_season != 4 and season != 4 and seasonTab[y][x] != season:
                        if random() < 0.2:
                            setObjectAt(x,y,getObjectAt(x,y) + season - last_season)
                            seasonTab[y][x] = season
                    if season == 4 and random() < 0.1:
                        setObjectAt(x,y,31)
                        seasonTab[y][x] = season                    

                    if random() < probaSuddenFire[season - 1]:
                        setObjectAt(x,y,burningTreeId)
                        seasonTab[y][x] = 0
                        continue
                    if random() < probaFire[season - 1]:
                        for neighbours in ((-1,0),(+1,0),(0,-1),(0,+1)):
                            if getObjectAt((x+neighbours[0]+worldWidth)%worldWidth,(y+neighbours[1]+worldHeight)%worldHeight) == burningTreeId:
                                setObjectAt(x,y,burningTreeId)
                                seasonTab[y][x] = 0
                                continue

                #snowed trees back to normal trees
                if getObjectAt(x,y) == 31:
                    if random() < 0.1:
                        if season != 4:
                            setObjectAt(x,y,choice([4,10,7,13]) + season - 1)
                            seasonTab[y][x] = season
                            continue

                #pine trees to snowed pine trees
                if getObjectAt(x,y) in (16,17,18,19,20):
                    if season == 4:
                        if random() < 0.05:
                            if getObjectAt(x,y) < 18:
                                setObjectAt(x,y,28)
                            else:
                                setObjectAt(x,y,27)
                            seasonTab[y][x] = 4
                            continue

                #halfway snowed pine trees to fully snowed pine trees
                if getObjectAt(x,y) in (27,28):
                    if season == 4:
                        cptTab[y][x] += 1
                        if cptTab[y][x] == 30:
                            setObjectAt(x,y,getObjectAt(x,y)+2)
                    else:
                        cptTab[y][x] -= 1
                        if cptTab[y][x] < 1:
                            if getObjectAt(x,y) == 28:
                                setObjectAt(x,y,choice([16,17]))
                            else:
                                setObjectAt(x,y,choice([18,19,20]))
                            cptTab[y][x] = 0
                            seasonTab[y][x] = season

                #fully snowed pine trees
                if getObjectAt(x,y) in (29,30):
                    if season != 4:
                        cptTab[y][x] -= 1
                        if cptTab[y][x] == 0:
                            setObjectAt(x,y,getObjectAt(x,y)-2)

                #grass catch fire
                if getObjectAt(x,y) >= 21 and getObjectAt(x,y) < 26: 
                    if random() < probaSuddenFire[season - 1]:
                        setObjectAt(x,y,burningGrassId)

                #grass on fire
                if getObjectAt(x,y) == burningGrassId: 
                    cptTab[y][x] += 1
                    if cptTab[y][x] == 15:
                        setObjectAt(x,y,0)
                        cptTab[y][x] = 0

                #trees on fire or ashes
                if getObjectAt(x,y) == burningTreeId or getObjectAt(x,y) == ashesId:
                    cptTab[y][x] = cptTab[y][x] + 1                    
                    if cptTab[y][x] == 25:
                        setObjectAt(x,y,ashesId)
                        cptTab[y][x] = cptTab[y][x] + 1
                    elif cptTab[y][x] == 30:
                        if random() < probaNewTree[season - 1] and season != 4:
                            setObjectAt(x,y,choice([4,7,10,13]) + season - 1)
                            seasonTab[y][x] = season
                        else:
                            setObjectAt(x,y,0)
                        cptTab[y][x] = 0

                #coin on normal ground
                if getObjectAt(x,y) >= coinId and getObjectAt(x,y) < coinId + 4: #coin or candy disappearing
                    cptTab[y][x] += 1
                    if cptTab[y][x] == 500:
                        setObjectAt(x,y,0)
                        cptTab[y][x] = 0

                #coin on edges
                if getObjectAt(x,y,1) >= coinId and getObjectAt(x,y,1) < coinId + 4:
                    cptTab[y][x] += 1
                    if cptTab[y][x] == 500:
                        setObjectAt(x,y,0,1)
                        cptTab[y][x] = 0
                if getObjectAt(x,y,2) >= coinId and getObjectAt(x,y,2) < coinId + 4 and getObjectAt(x,y,1) != 33:
                    cptTab[y][x] += 1
                    if cptTab[y][x] == 500:
                        setObjectAt(x,y,0,2)
                        cptTab[y][x] = 0

                if getObjectAt(x,y,1) == rockId and season == 4:
                    setObjectAt(x,y,snowmanId,1)

                if getObjectAt(x,y,1) == snowmanId and season != 4:
                    setObjectAt(x,y,rockId,1)

                #if y >= 0 and y < 15:
                #    for level in range(objectMapLevels-3):
                #        cur_ob = getObjectAt(x,y,level)
                #        higher_ob = getObjectAt(x,y,level + 1)
                #        if season == 4 and cur_ob == 33 \
                #        and (higher_ob == 0 or (higher_ob >= 48 and higher_ob < 52) or (higher_ob >= 56 and higher_ob < 60) \
                #            or (higher_ob >= coinId and higher_ob < coinId + 4)):
                #            setObjectAt(x,y,35,level)

                #water coming down from mountain
                if flow ==True and x >= 0 and x < 20 and y >= 0 and y < 15: #water from lake on mountain
                    for level in range(objectMapLevels-3):
                        cur_ob = getObjectAt(x,y,level)
                        if cur_ob in (49,48): #top of waterfall
                            l = level
                            if cur_ob == 49:
                                n = (0,-1)
                            else:
                                n = (-1,0)
                            while getObjectAt(x+n[0],y+n[1],l) not in (0,cur_ob + 38):
                                l += 1
                            if getObjectAt(x+n[0],y+n[1],l) == cur_ob + 38:
                                setObjectAt(x,y,cur_ob + 18,level)

                        if cur_ob in (57,56) and (getObjectAt(x,y,level+1) == cur_ob + 10 or getObjectAt(x,y,level+1) == cur_ob + 14): #mid of waterfall
                            setObjectAt(x,y,cur_ob + 14,level)

                        if cur_ob == 33 and getObjectAt(x,y,level+1) != 33 and getObjectAt(x,y,level+1) != 32\
                        and (getObjectAt(x,y,level+1) in (67,66,71,70) \
                        or getObjectAt(x,y+1,level+2) == 60 or getObjectAt(x+1,y,level+2) == 60 \
                        or getObjectAt(x-1,y,level+2) == 60 or getObjectAt(x,y-1,level+2) == 60): #water spreading on mountain

                            l = 0
                            while getObjectAt(x,y,l) == 33: #highest not edge level 
                                l = l + 1
                            edge_level = 0
                            if getObjectAt(x,y,l + edge_level) != 0:
                                while getObjectAt(x,y,l + edge_level) != 0:
                                    edge_level = edge_level + 1
                            i = 0
                            while i <= edge_level: #set edges to 2 levels higher to make place for added tiles
                                setObjectAt(x,y,getObjectAt(x,y,l+edge_level-i),l+edge_level-i+2)
                                i = i + 1
                            l = l - 1
                            #replace a ground tile of full thickness with 1 ground tile of 1/2 thickness + 1 ground tile of 1/4 thickness + 1 water tile of 1/4 thickness
                            #an empty object between 2 layers of non-empty objects not allowed 
                            setObjectAt(x,y,32,l)
                            setObjectAt(x,y,34,l+1)
                            # if near edge, make entrance, if not, just add water
                            if getObjectAt(x,y+1,l) == 49:
                                setObjectAt(x,y,87,l+2)
                            elif getObjectAt(x+1,y,l) == 48:
                                setObjectAt(x,y,86,l+2)
                            else:                    
                                setObjectAt(x,y,60,l+2)

                    if getObjectAt(x,y) in (67,66,71,70): #water spreading at foot of mountain
                        level = 0
                        while getObjectAt(x,y,level) != 0:
                            level += 1                            
                        while level > 0:
                            setObjectAt(x,y,getObjectAt(x,y,level-1),level)  
                            level -= 1
                        setObjectAt(x,y,60)
                        setTerrainAt(x,y,2)
                        setHeightAt(x,y,6)
                        flow_height = 6

                #water spreading on ground
                if flow == True and it % 20 == 0 and water_on_mount > 0 and random() < 0.5:
                    if getTerrainAt(x,y) in (0,7) and (getObjectAt(x,y) == 0 or (getObjectAt(x,y) >= coinId and getObjectAt(x,y) < coinId + 4)) :
                        neighbours = ((+1,0),(+1,+1),(0,+1),(-1,+1),(-1,0),(-1,-1),(0,-1),(+1,-1))
                        mountain_center = (6,4)
                        i = 0
                        while i < 8 and not (getObjectAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight()) == 60 \
                                    and getHeightAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight()) >= getHeightAt(x,y)\
                                    and drops > 0 and getHeightAt(x,y) >= flow_height):
                            i += 1
                        if i < 8:                         
                            setObjectAt(x,y,getObjectAt(x,y),1)
                            setObjectAt(x,y,60)
                            drops -= 1                                   
                            water_on_mount -= 1
                            #else:
                            #    if getTerrainAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight()) in (0,7):
                            #        if getHeightAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight()) > getHeightAt(x,y):
                            #            setObjectAt(x,y,getObjectAt(x,y),1)
                            #            setObjectAt(x,y,60)
                            #            setObjectAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight(),\
                            #                getObjectAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight(),1))                                        
                            #            drops -= 1
                            #        elif getHeightAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight()) == getHeightAt(x,y):
                            #            cur_ray = (x - mountain_center[0])*(x - mountain_center[0]) + (y - mountain_center[1])*(y - mountain_center[1])
                            #            nei_ray = ((x+neighbours[i][0])%getWorldWidth() - mountain_center[0])*((x+neighbours[i][0])%getWorldWidth() - mountain_center[0]) \
                            #                    + ((y+neighbours[i][1])%getWorldHeight() - mountain_center[1])*((y+neighbours[i][1])%getWorldHeight() - mountain_center[1])
                            #            if cur_ray >= nei_ray:
                            #                setObjectAt(x,y,getObjectAt(x,y),1)
                            #                setObjectAt(x,y,60)
                            #                setObjectAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight(),\
                            #                    getObjectAt((x+neighbours[i][0])%getWorldWidth(),(y+neighbours[i][1])%getWorldHeight(),1))
                            #                drops -= 1

    return

### ### ### ### ###

def stepAgents( it = 0 ):
    # move agents
    global dropper,nbPreda,nbPrey
    if it % (maxFps/10) == 0:
        nb_prey = 0
        nb_pred = 0
        prey_caught_positions = []
        prey_eaten_positions = []
        nba = len(agents)
        i = 0
        shuffle(agents)
        while i < nba:
            x = agents[i].x
            y = agents[i].y
            cpt = agents[i].cpt
            if agents[i].getType() in (preyId,preyId + 1,preyId + 2) :
                if cpt < lifeCyclePrey:
                    if getObjectAt(x,y) in (60,61) and season != 4:
                        if verbose == True:
                            print("prey drowned at x = ",x," y = ",y)
                        setAgentAt(x,y,0)
                        del agents[i]
                        nba -= 1                        
                    else:
                        if cpt == 10 :
                            agents[i].type = preyId + 1
                            setAgentAt(x,y,preyId + 1)
                        if cpt == lifeCyclePrey - 20:
                            agents[i].type = preyId + 2
                            setAgentAt(x,y,preyId + 2)
                        if random() < probaAgentMove[season - 1]:
                            agents[i].movePrey()
                        nb_prey += 1
                        i += 1
                else:
                    if verbose == True:
                        print("prey starved to death at x = ",x," y = ",y," i = ",i)
                    setAgentAt(x,y,0)
                    del agents[i]
                    nba -= 1
            else:
            #predators die before moving -> no catching prey after dying or dying after catching prey
                if cpt < lifeCyclePreda:
                    if getObjectAt(x,y) in (60,61) and season != 4:
                        if verbose == True:
                            print("predator drowned at x = ",x," y = ",y)
                        setAgentAt(x,y,0)
                        del agents[i]
                        nba -= 1
                    else:
                        if cpt == 10:
                            agents[i].type = predaId +1
                            setAgentAt(x,y,predaId+1)
                        if cpt == lifeCyclePreda - 60:
                            agents[i].type = predaId + 2
                            setAgentAt(x,y,predaId+2)
                        nb_pred += 1
                        if random() < probaAgentMove[season - 1]:
                            res = agents[i].movePreda()
                        else:
                            res = (-1,-1)
                        if res != (-1,-1):
                            prey_caught_positions.append(res)
                        i += 1
                else:
                    if verbose == True:
                        print("predator starved to death at x = ",x," y = ",y," i = ",i)
                    setAgentAt(x,y,0)
                    del agents[i]
                    nba -= 1

        nbPrey = nb_prey
        nbPreda = nb_pred
        if verbose == True:
            print (nb_prey," preys left ",nb_pred," predators left")
        for p in prey_caught_positions:
            nba = len(agents)
            i = 0
            while i < nba:
                x = agents[i].x
                y = agents[i].y
                if agents[i].getType() in (preyId,preyId + 1,preyId + 2):
                    if (x,y) == p:
                        if verbose == True:
                            print("prey at x = ",x," y = ",y," got eaten i = ",i)
                        prey_eaten_positions.append(p)
                        del agents[i]
                        i = nba
                i += 1
        for p in prey_eaten_positions:
            for a in agents:
                if a.getPosition() == p:
                    if verbose == True:
                        print("predator ate after ",a.cpt)
                    a.cpt = 0
                    a.type = predaId + 1

        if 'dropper' in globals():
            if dropper.cpt < lifeCycleDropper:
                if getObjectAt(dropper.x,dropper.y) in (60,61) and season != 4:
                    setAgentAt(dropper.x,dropper.y,noAgentId)
                    del dropper
                    print("dropper drowned") 
                else:                   
                    if verbose == True:
                        print("cpt = ",dropper.cpt)
                    dropper.moveDropper()
            else:
                setAgentAt(dropper.x,dropper.y,noAgentId)
                del dropper
                print("dropper died of not being able to move")
        if random() < probaPreyBorn[season - 1] and nb_prey > 0:
            agents.append(BasicAgent(preyId))
            if verbose == True:
                print("new prey at x = ",agents[-1].x," y = ",agents[-1].y)
        if random() < probaPredBorn[season - 1] and nb_pred > 0:
            agents.append(BasicAgent(predaId))
            if verbose == True:
                print("new predator at x = ",agents[-1].x," y = ",agents[-1].y)            
    return

def lastMessage (text,endtype):
    #print("message printed")
    if endtype == 1:
        screen.fill((255,0,0))
    elif endtype == 2:
        screen.fill((240,128,128))
    elif endtype == 3:
        screen.fill((47 ,79 ,79 ))
    screen.blit(text,(screenWidth/2-100,screenHeight/2-10))

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

timestamp = datetime.datetime.now().timestamp()
time_start_lm = 0
dpy_lm = False
text_lm = None
gameEnd = 0

loadAllImages()

displayWelcomeMessage()

initWorld()
initAgents()

player  = BasicAgent(playerId,8,7)
dropper = Dropper(dropperId)

print ("initWorld:",datetime.datetime.now().timestamp()-timestamp,"second(s)")
timeStampStart = timeStamp = datetime.datetime.now().timestamp()

it = itStamp = 0

userExit = False

while userExit == False:

    if it != 0 and it % 100 == 0 and verboseFps:
        print ("[fps] ", ( it - itStamp ) / ( datetime.datetime.now().timestamp()-timeStamp ) )
        timeStamp = datetime.datetime.now().timestamp()
        itStamp = it
    if it != 0 and it % 500 == 0:
        last_season = season
        season = season % 4 + 1
        setSeason(season)

    render(it)
    
    screen.blit(imagesShown[0],(5,5))
    if gameEnd == 0:
        text_player_pos = font.render(str(player.getPosition()),True,(255,255,255))
        screen.blit(text_player_pos,(50, 5))

    screen.blit(imagesShown[1],(180,10))
    text_nb_coin = font.render('x '+str(nbCoin),True,(255,255,255))
    screen.blit(text_nb_coin,(210, 5))    

    screen.blit(imagesShown[5],(280,3))
    text_nb_coin = font.render('x '+str(nbKilled),True,(255,255,255))
    screen.blit(text_nb_coin,(325, 5)) 

    screen.blit(imagesShown[2],(3,30))
    if 'dropper' in globals():
        text_dropper_pos = font.render(str(dropper.getPosition()),True,(255,255,255))

    else:
        text_dropper_pos = font.render('dead',True,(255,255,255))
    screen.blit(text_dropper_pos,(50, 30))
    
    screen.blit(imagesShown[3],(5,57))
    text_nb_prey = font.render('x '+str(nbPrey),True,(255,255,255))
    screen.blit(text_nb_prey,(50, 57))

    screen.blit(imagesShown[4],(5,82))
    text_nb_pred = font.render('x '+str(nbPreda),True,(255,255,255))
    screen.blit(text_nb_pred,(50, 84))


    screen.blit(text_season[season-1],(10,110))

    stepWorld(it)
    stepAgents(it)


    ind_agent = 0
    nba = len(agents)
    if gameEnd == 0:
        while ind_agent < nba and agents[ind_agent].getPosition() != player.getPosition():
            ind_agent += 1
        if ind_agent < nba:
            if agents[ind_agent].getPosition() == player.getPosition():
                if agents[ind_agent].type in (predaId, predaId + 1, predaId + 2):
                    nbCoin -= 10
                    if nbCoin >= 0:
                        nbKilled += 1
                        del agents[ind_agent]
                        setAgentAt(player.x,player.y,playerId)
                    else:
                        print("couldnt kill predator")
                        del player
                        gameEnd = 1
                        break

    if gameEnd == 0:
        level = 0
        for l in range(objectMapLevels):
            if getObjectAt(player.x,player.y,l) == 0:
                level = l - 1
                break

        if getObjectAt(player.x,player.y,level) in (60,61) and season != 4:
            print("player drowned")
            del player
            gameEnd = 3

    if gameEnd == 0:
        if getObjectAt(player.x,player.y,level) in (rockId,snowmanId):
            if nbKilled >= 1:
                print("won")
                del player
                gameEnd = 2

    if gameEnd == 1 and dpy_lm == False: #player got killed by predator
        dpy_lm = True
        text_lm = font.render('game over ;(',True,(0,0,0))
        time_start_lm = datetime.datetime.now().timestamp()
        print ("game end time start = ", time_start_lm)

    if gameEnd == 2 and dpy_lm == False: #game won
        dpy_lm = True
        text_lm = font.render('you\'ve won \\^o^/',True,(255,255,255))
        time_start_lm = datetime.datetime.now().timestamp()
        print ("game end time start = ", time_start_lm)
        
    if gameEnd == 3 and dpy_lm == False: #player drowned
        dpy_lm = True
        text_lm = font.render('you\'ve drowned ~~\\o/~~',True,(255,255,255))
        time_start_lm = datetime.datetime.now().timestamp()
        print ("game end time start = ", time_start_lm)

    if dpy_lm:
        lastMessage(text_lm,gameEnd)
        #print("tick tock = ",datetime.datetime.now().timestamp() - time_start_lm)
        if datetime.datetime.now().timestamp() - time_start_lm > 4:
            break

    if not hidden_steps and water_on_mount == 0 and waterfalls[3] == True:
        setTerrainAt(13,10,1)
        setHeightAt(13,10,3)
        setObjectAt(13,10,99,0)
        setObjectAt(13,10,0,1)
        setObjectAt(13,10,0,2)
        setObjectAt(13,9,99,1)
        setObjectAt(13,9,0,2)
        setObjectAt(13,9,0,3)
    
    # continuous stroke
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        xViewOffset  = (xViewOffset - 1 + getWorldWidth() ) % getWorldWidth()
        if verbose:
            print("View at (",xViewOffset ,",",yViewOffset,")")
    elif keys[pygame.K_RIGHT] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        xViewOffset = (xViewOffset + 1 ) % getWorldWidth()
        if verbose:
            print("View at (",xViewOffset ,",",yViewOffset,")")
    elif keys[pygame.K_DOWN] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        yViewOffset = (yViewOffset + 1 ) % getWorldHeight()
        if verbose:
            print("View at (",xViewOffset,",",yViewOffset,")")
    elif keys[pygame.K_UP] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ):
        yViewOffset = (yViewOffset - 1 + getWorldHeight() ) % getWorldHeight()
        if verbose:
            print("View at (",xViewOffset,",",yViewOffset,")")
    elif keys[pygame.K_k] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ) and gameEnd == 0:
        player.movePlayer(0,+1);
    elif keys[pygame.K_i] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ) and gameEnd == 0:
        player.movePlayer(0,-1);
    elif keys[pygame.K_l] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ) and gameEnd == 0:
        player.movePlayer(+1,0);
    elif keys[pygame.K_j] and not ( keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] ) and gameEnd == 0:
        player.movePlayer(-1,0);

    # single stroke
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYUP:
            if event.key == K_ESCAPE:
                userExit = True
            elif event.key == pygame.K_k and gameEnd == 0:
                player.movePlayer(0,+1);
            elif event.key == pygame.K_i and gameEnd == 0:
                player.movePlayer(0,-1);
            elif event.key == pygame.K_l and gameEnd == 0:
                player.movePlayer(+1,0);
            elif event.key == pygame.K_j and gameEnd == 0:
                player.movePlayer(-1,0);                
            elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                addNoise = not(addNoise)
                print ("noise is",addNoise) # easter-egg
            elif event.key == pygame.K_v:
                verbose = not(verbose)
                print ("verbose is",verbose)
            elif event.key == pygame.K_f:
                verboseFps = not(verboseFps)
                print ("verbose FPS is",verboseFps)
            elif event.key == pygame.K_p:
                last_season = season
                season = 1
                setSeason(season)
                print ("Spring")
            elif event.key == pygame.K_e:     
                last_season = season           
                season = 2
                setSeason(season)
                print ("Summer")
            elif event.key == pygame.K_a:
                last_season = season
                season = 3
                setSeason(season)
                print ("Fall")
            elif event.key == pygame.K_h:
                last_season =season
                season = 4
                setSeason(season)
                print ("winter") 
            elif event.key == pygame.K_w:                 
                if season != 4 and waterfalls != [True]*4 and water_on_mount > 0:
                    flow = True
                    ways = [0,1,2,3]
                    shuffle(ways)
                    i = 0
                    while waterfalls[ways[i]]:
                        i += 1
                    waterfalls[ways[i]] = True
                    print("water flows ",ways[i])
                    if ways[i] == 0:
                        setObjectAt(3,7,87,6)
                    elif ways[i] == 1:
                        setObjectAt(4,7,87,6)             
                    elif ways[i] == 2:
                        setObjectAt(6,6,87,6)
                        setObjectAt(7,6,77,6)
                        setObjectAt(6,5,61,6)
                        setObjectAt(7,5,79,6)
                    elif ways[i] == 3:
                        setObjectAt(8,5,80,6)
                        setObjectAt(9,5,86,6)
                        setObjectAt(8,4,78,6)
                        setObjectAt(9,4,76,6)
            elif event.key == pygame.K_LEFT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                xViewOffset  = (xViewOffset - 1 + getWorldWidth() ) % getWorldWidth()
                if verbose:
                    print("View at (",xViewOffset ,",",yViewOffset,")")
            elif event.key == pygame.K_RIGHT and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                xViewOffset = (xViewOffset + 1 ) % getWorldWidth()
                if verbose:
                    print("View at (",xViewOffset ,",",yViewOffset,")")
            elif event.key == pygame.K_DOWN and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                yViewOffset = (yViewOffset + 1 ) % getWorldHeight()
                if verbose:
                    print("View at (",xViewOffset,",",yViewOffset,")")
            elif event.key == pygame.K_UP and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                yViewOffset = (yViewOffset - 1 + getWorldHeight() ) % getWorldHeight()
                if verbose:
                    print("View at (",xViewOffset,",",yViewOffset,")")
            elif event.key == pygame.K_o and not( pygame.key.get_mods() & pygame.KMOD_SHIFT ) :
                if viewWidth > 1:
                    viewWidth = int(viewWidth / 2)
                    viewHeight = int(viewHeight / 2)
                if verbose:
                    print ("View surface is (",viewWidth,",",viewHeight,")")
            elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                if viewWidth * 2 < worldWidth :
                    viewWidth = viewWidth * 2
                    viewHeight = viewHeight * 2
                    #if scaleMultiplier 
                else:
                    viewWidth = worldWidth
                    viewHeight = worldHeight
                if verbose:
                    print ("View surface is (",viewWidth,",",viewHeight,")")
            elif event.key == pygame.K_s and not( pygame.key.get_mods() & pygame.KMOD_SHIFT ) :
                if scaleMultiplier > 0.15:
                    scaleMultiplier = scaleMultiplier / 2
                if scaleMultiplier < 0.15:
                    scaleMultiplier = 0.15                   
                resetImages()
                if verbose:
                    print ("scaleMultiplier is ",scaleMultiplier)
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                if scaleMultiplier < 1.2:
                    scaleMultiplier = scaleMultiplier * 2
                if scaleMultiplier > 1.2:
                    scaleMultiplier = 1.2
                resetImages()
                if verbose:
                    print ("scaleMultiplier is ",scaleMultiplier)

    pygame.display.flip()
    fpsClock.tick(maxFps) # recommended: 30 fps

    it += 1

fps = it / ( datetime.datetime.now().timestamp()-timeStampStart )
print ("[Quit] (", fps,"frames per second )")

pygame.quit()
sys.exit()
