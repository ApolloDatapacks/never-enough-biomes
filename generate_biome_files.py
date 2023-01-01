import math
import os

## gridLength controls the number of temperature and downfall parameters. 
## a gridLength of 25 = 25 temperature intervals and 25 downfall intervals, leading to 625 biomes.
## some strange numbers like 7 won't work. Multiples of 10 with 1 added work well.
gridLength = 31
## the namespace all the custom files will be under.
namespace = "apollo"


parameters = "{\"type\":\"minecraft:overworld\",\"generator\":{\"type\":\"minecraft:noise\",\"settings\":\"minecraft:overworld\",\"biome_source\":{\"type\":\"minecraft:multi_noise\",\"biomes\":["
peaks =  {
    'a1':'snowy_plain','a2':'snowy_plains','a3':'snowy_plains','a4':'snowy_taiga','a5':'snowy_taiga',
    'b1':'plains','b2':'plains','b3':'forest','b4':'taiga','b5':'old_growth_taiga',
    'c1':'plains','c2':'plains','c3':'forest','c4':'birch_forest','c5':'dark_forest',
    'd1':'savanna','d2':'plains','d3':'sparse_jungle','d4':'jungle','d5':'jungle',
    'e1':'desert','e2':'desert','e3':'desert','e4':'desert','e5':'desert',
}

# General utility functions
def deleteFilesInFolder(folder):
    for item in os.listdir(folder):
        itemPath = os.path.join(folder, item)
        if os.path.isfile(itemPath):
            os.remove(itemPath)

def createFolder(path):
    if os.path.exists(path):
        pass
    else: 
        os.mkdir(path)

# Worldgen functions that need to be repeated

# def findPeaks(primaryValue, secondaryValue, primaryOffset):
    # Peak = round(4*(primaryValue+primaryOffset))-
    # PeakDistance = round(100*((1.5-(4*abs((math.ceil(4*primaryValue)/4)+0.125-primaryValue)))),3)
    # PeakBiome = peaks[str(chr(round(4*(secondaryValue-(0.5)))+99))+str(Peak+3)]
    # return PeakDistance, PeakBiome

def findPeaksDiagonal(downfall, temperature, downfallOffset, temperatureOffset):
    Peak = str(chr(round(4*(temperature-temperatureOffset))+99))+str(round(4*(downfall-downfallOffset))+3)
    PeakBiome = peaks[Peak]
    PeakDistanceDownfall = 4*abs(math.floor(4*downfall)/4-downfall)
    PeakDistanceTemperature = 4*abs(math.floor(4*temperature)/4-temperature)

    if downfallOffset == 0.624:
        PeakDistanceDownfall = 1 - PeakDistanceDownfall
    
    if temperatureOffset == 0.624:
        PeakDistanceTemperature = 1 - PeakDistanceTemperature

    PeakDistanceTotal = round(100* PeakDistanceDownfall * PeakDistanceTemperature,4)
    return PeakDistanceTotal, PeakBiome


def generateBiome(downfall, temperature, fileName):
    with open("data/"+namespace+"/worldgen/biome/"+fileName+".json", "w") as json:
        biomeInfo = "{\"temperature\":"+str(temperature+0.05)+",\"downfall\":"+str(downfall+0.05)+",\"precipitation\":\"rain\",\"effects\":{\"sky_color\":7907327,\"fog_color\":12638463,\"water_color\":4159204,\"water_fog_color\":329011},\"spawners\":{},\"spawn_costs\":{},\"carvers\":{},\"features\":[[],[],[],[],[],[],[],[],[],[\""+namespace+":vegetation_"+fileName+"\"],[\"minecraft:freeze_top_layer\"]]}"
        json.write(biomeInfo)

def generateFeatures(downfall, temperature, fileName):

    #ld = lowDownfall, hd = highDownfall, lt = lowTemperature, ht = highTemperature
    ldltPeakDistance, ldltPeakBiome = findPeaksDiagonal(downfall, temperature, 0.624, 0.624)
    ldhtPeakDistance, ldhtPeakBiome = findPeaksDiagonal(downfall, temperature, 0.624, 0.376)
    hdltPeakDistance, hdltPeakBiome = findPeaksDiagonal(downfall, temperature, 0.376, 0.624)
    hdhtPeakDistance, hdhtPeakBiome = findPeaksDiagonal(downfall, temperature, 0.376, 0.376)

    ## print("Temperature: "+str(temperature)+", Downfall: "+str(downfall)+" || Top left biome is "+str(ldltPeakDistance)+"% "+ldltPeakBiome+", top right biome is "+str(hdltPeakDistance)+"% "+hdltPeakBiome+", bottom left biome is "+str(ldhtPeakDistance)+"% "+ldhtPeakBiome+", bottom right biome is "+str(hdhtPeakDistance)+"% "+hdhtPeakBiome)
    with open("data/"+namespace+"/worldgen/placed_feature/vegetation_"+fileName+".json", "w") as json:
        json.write("{\"feature\":\""+namespace+":vegetation_"+fileName+"\",\"placement\":[{\"type\":\"minecraft:count\",\"count\":100},{\"type\":\"minecraft:in_square\"},{\"type\":\"minecraft:biome\"}]}")

    with open("data/"+namespace+"/worldgen/configured_feature/vegetation_"+fileName+".json", "w") as json:
        currentRemainingChance = 100
        configuredFeatureInfo = ("{\"type\":\"minecraft:random_selector\",\"config\":{\"features\":[{\"chance\":"+str(round(ldltPeakDistance/currentRemainingChance,5))+",\"feature\":\"apollo:vegetation/"+ldltPeakBiome)
        currentRemainingChance = currentRemainingChance - ldltPeakDistance
        if currentRemainingChance == 0 or ldhtPeakDistance == 0:
            pass
        else:
            configuredFeatureInfo = configuredFeatureInfo + ("\"},{\"chance\":"+str(round(ldhtPeakDistance/currentRemainingChance,5))+",\"feature\":\"apollo:vegetation/"+ldhtPeakBiome)
            currentRemainingChance = currentRemainingChance - ldhtPeakDistance
        
        if currentRemainingChance == 0 or hdltPeakDistance == 0:
            pass
        else:
            configuredFeatureInfo = configuredFeatureInfo + ("\"},{\"chance\":"+str(round(hdltPeakDistance/currentRemainingChance,5))+",\"feature\":\"apollo:vegetation/"+hdltPeakBiome)
            currentRemainingChance = currentRemainingChance - hdltPeakDistance
        
        if currentRemainingChance == 0 or hdhtPeakDistance == 0:
            pass
        else:
            configuredFeatureInfo = configuredFeatureInfo + ("\"},{\"chance\":"+str(round(hdhtPeakDistance/currentRemainingChance,5))+",\"feature\":\"apollo:vegetation/"+hdhtPeakBiome)
        
        configuredFeatureInfo = configuredFeatureInfo + ("\"}],\"default\":{\"feature\":{\"type\":\"minecraft:no_op\",\"config\":{}},\"placement\":[]}}}")
        json.write(configuredFeatureInfo)

# Generate all needed folders
createFolder(".\data\\"+namespace)
createFolder(".\data\\"+namespace+"\worldgen")
createFolder(".\data\\"+namespace+"\worldgen\\biome")
createFolder(".\data\\"+namespace+"\worldgen\configured_feature")
createFolder(".\data\\"+namespace+"\worldgen\placed_feature")

# Delete all current biome/placed feature/configured feature data
deleteFilesInFolder(r'.\data\{}\worldgen\biome'.format(namespace))
deleteFilesInFolder(r'.\data\{}\worldgen\configured_feature'.format(namespace))
deleteFilesInFolder(r'.\data\{}\worldgen\placed_feature'.format(namespace))

# Actually generate the biomes
temperature = 0.0
downfall = 0.0

while temperature <= 1.0:
    while downfall <= 1.0:
        fileName = str(downfall)+"_"+str(temperature)
        generateBiome(downfall, temperature, fileName)
        generateFeatures(downfall, temperature, fileName)
        parameters = parameters + "{\"biome\":\""+namespace+":"+str(downfall)+"_"+str(temperature)+"\",\"parameters\":{\"temperature\":"+str(round(2*(temperature-0.5),2))+",\"humidity\":"+str(round(2*(downfall-0.5),2))+",\"continentalness\":0,\"erosion\":0,\"weirdness\":0,\"depth\":0,\"offset\":0}},"
        downfall = round((downfall + (1/(gridLength-1))),2)
    temperature = round((temperature + (1/(gridLength-1))),2)
    downfall = 0.0

parameters = parameters[:-1] + "]}}}"
with open("data/minecraft/dimension/overworld.json", "w") as json:
    json.write(parameters)