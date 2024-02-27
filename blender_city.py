import bpy
import bmesh
from random import randint


def main():

    # clear the scene
    clear_old()

    # spacing between buildings
    spacing = 2.3

    # generates location data to create a grid
    for x in range(10):
        for y in range(10):
            location = (x * spacing, y * spacing,0)
            building(location)
    
    # adds color        
    colorize()
    

    
"""
    Deletes the old city
"""
def clear_old():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


""" params: location- position the object will be created at
    Creates a mesh object and data then create the vertices and faces of the building
"""
def building(location):
    
    obj_name = "building"

    # create mesh data
    mesh_data = bpy.data.meshes.new(f"{obj_name}_data")

    # create mesh object with mesh data
    mesh_obj = bpy.data.objects.new(obj_name, mesh_data)

    # add mesh object to the scene
    bpy.context.scene.collection.objects.link(mesh_obj)

    # starts bmesh, which is the mesh editor module
    bm = bmesh.new()
    
    # gets a random height for this building
    height = define_height()
    
    # creates verts (vertices, the corners of the rectangle) for the bottom and top faces
    bottom_verts = create_verts(bm,location,0)
    top_verts = create_verts(bm,location,height)
    
    # create the faces of the triangle
    create_faces(bm,top_verts,bottom_verts)
    add_topper(bm,top_verts,location,height)

    # updates the mesh object with the new meshes we made and clears bmesh
    bm.to_mesh(mesh_data)
    mesh_data.update()
    bm.free()


""" Determines if a building is tall or not and assigns random height if it is
    returns: height of building object
"""
def define_height():
    
    # half of the buildings will be tall, and half will only have a height of 1
    tall = randint(0,1)
    height = 1
    
    # if the building is tall, gets a random height
    if tall:
        height += randint(3,10)
    return height


""" params: bm - mesh object
            location - coordinates of the center of the top and bottom faces
            height - height of the building
            topper_inset - if building has a topper, this is the inset from the lower floors top edges. default is 0
            tiers - the number of tiers to the building. multiplied by topper_inset to create smaller topper tiers default is 1
    Creates a list of vertices that will be the bottom or top face of a building or topper tier. 1 is added or subtracted from the location 
    x and y coordinates to get each vertex. if height is 0, is the bottom face of a building or topper. if there is a height, it is the top face
    topper_inset is multiplied by the number of tiers. If it is more than one, it insets each topper layer making each one smaller
    returns: 
"""
def create_verts(bm, location, height, topper_inset = 0, tiers = 1):    
    
        # creates a list of coordinates
        verts = [
            (location[0] + 1 + topper_inset * tiers, location [1] + 1 + topper_inset * tiers, height),
            (location[0] + 1 + topper_inset * tiers, location [1] + -1 - topper_inset * tiers, height),
            (location[0] + -1 - topper_inset * tiers, location [1] + -1 - topper_inset * tiers, height),
            (location[0] + -1 - topper_inset * tiers, location [1] + 1 + topper_inset * tiers, height)]
            
        # converts each coordinate to a vertex
        verts = [bm.verts.new(x) for x in verts]
        return verts    


"""
    params: bm - mesh object
            top = list of vertices for top face
            bottom = list of vertices for bottom face
    Creates all faces of the building or topper using the vertices of the top and bottom faces
"""
def create_faces(bm,top,bottom):
    
    # bottom face
    bm.faces.new((bottom[0],bottom[1],bottom[2],bottom[3]))
    # front face
    bm.faces.new((top[2],top[1],bottom[1],bottom[2]))
    # back face
    bm.faces.new((top[3],top[0],bottom[0],bottom[3]))
    # left face
    bm.faces.new((top[3],top[2],bottom[2],bottom[3]))
    # right face
    bm.faces.new((top[1],top[0],bottom[0],bottom[1]))
    # top face
    bm.faces.new((top[0],top[1],top[2],top[3]))
    

"""
    params: bm - mesh object
            top = list of vertices for top face
            location - coordinates of the center of the top and bottom faces
            height - height of the building
    Determines which topper a building could have based on its height then determines if it should have a topper at all.
    If so, calls make_topper() with appropriate parameters based on it being tall or short. Buildings with no height of 1 
    are neither short or tall and don't get toppers
"""
def add_topper(bm, top, location, height):
    
    # determines if tall or short or neither
    is_tall = height > 7
    is_short = 1 < height <= 7
    
    # checks if building will have a topper
    if has_topper():
        #tall buildings get 3 tiered toppers
        if is_tall:
            make_topper(bm,location,height,.3,-.2,3)
        #short buildings get 1 tier toppers
        elif is_short:
            make_topper(bm,location,height,.3,-.2,1)

"""
    Chooses if a building will have a topper or not. Half of buildings get toopers
    returns: 0 or 1, which is used to evaluate truthiness
"""       
def has_topper():
    return randint(0,1)
    
"""
    params: bm - mesh object
            location - coordinates of the center of the top and bottom faces
            height - height of the building
            topper_height - the height of a topper tier
            topper_inset - how far topper tiers will be inset from the floor below
            tiers - the total number of topper tiers to be created and how many times the recursive function is called
            tiers_built - how many tiers have been built so far and used to multiply topper_inset for multiple tiers. default is 0
    Calls create_verts() and create_faces() to create a topper tier. Each time it is run, it increments tiers_built
    by 1, increasing the inset from the building edge by topper_inset amount. Also decrements tiers. As long as tiers is 
    more than zero, this function is called recursively
"""
def make_topper(bm, location, height, topper_height, topper_inset, tiers, tiers_built = 0):
    
    # the first time this is called, default will be zero. 1 is set so that it can be multiplied
    if not tiers_built:
        tiers_built = 1
        
    # else tiers_built increments
    else:
        tiers_built += 1
        
    # if tiers is 0, all tiers have been made and function stops
    if tiers:
        
        # counts dows tiers
        tiers -= 1
        
        # creates the vertices for top and bottom faces of the topper
        topper_top = create_verts(bm,location,height+topper_height,topper_inset,tiers_built)
        topper_bot = create_verts(bm,location,height,topper_inset,tiers_built)
        
        # creates the all faces using vertex lists
        create_faces(bm,topper_top,topper_bot)
        
        # adds height for the next topper tier top vertices
        height = height + topper_height
        
        # recurively calls itself
        make_topper(bm,location,height,topper_height,topper_inset,tiers,tiers_built)
    
"""
    Adds random colors from scene materials list to buildings with height greater than 1. Buildings with height of 1
    are all given the same color.
"""
def colorize():
    
    # loops through each building
    for x in bpy.data.objects:
        
        # otherwise, it gets a random color from scene materials
        if x.dimensions[2] < 2:
            x.data.materials.append(bpy.data.materials[0])
            
        # all buildings that are not tall or short (height < 2) are one color
        # otherwise, it gets a random color from scene materials
        else:
            x.data.materials.append(bpy.data.materials[randint(1,3)])


main()
