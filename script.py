import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """

def first_pass( commands ):

    name = ''
    num_frames = 1

    for cmd in commands:
        isVary = False
        if cmd['op'] == 'frames':
            num_frames = int(cmd['args'][0])
        if cmd['op'] == 'basename':
            name = cmd['args'][0]
        elif cmd['op'] == 'vary':
            isVary = True

    if isVary == True and num_frames == 1:
        exit()
    
    if num_frames > 1 and name == '':
        name = 'default_name'
        print ('default name set to default_name')
        

    return (name, num_frames)

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass( commands, num_frames ):
    frames = [ {} for i in range(num_frames) ]

    for cmd in commands:
        if cmd['op'] == 'vary':
            knobName = cmd['knob']
            #print knobName
            knobArgs = cmd['args']
                
            start_frame = int(knobArgs[0])
            #print start_frame
            end_frame = int(knobArgs[1])
            #print end_frame
            start_val = int(knobArgs[2])
            #print start_val
            end_val = int(knobArgs[3])
            #print end_val
            scaling_range = end_val - start_val
            #print scaling_range
            scaling_factor = float(scaling_range) / float(end_frame-start_frame+1)
            #print scaling_factor

            try:
                scaling_vary = knobArgs[4]
            except IndexError:
                knobArgs.append(1)
                scaling_vary = 1
                print ('Vary Factor not found, setting to default value: 1')
                pass
            if knobArgs[4] <= 0:
                print ('Vary Factor value less than 0, setting to default value: 1')
                scaling_vary = 1
            else:
                scaling_vary = knobArgs[4]
            
            for i in range(start_frame, end_frame + 1):
                frames[i][knobName] = ((1/scaling_range)**(scaling_vary))*(scaling_factor)*(i**(scaling_vary + 1))
                #Equation created using desmos and can be found at https://www.desmos.com/calculator/wjpvgogb0b

    #print frames
    return frames


def run(filename):
    """
    This function runs an mdl script
    """
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print ("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    (name, num_frames) = first_pass(commands)
    frames = second_pass(commands, num_frames)

    for i in range( int(num_frames) ):
        tmp = new_matrix()
        ident( tmp )

        stack = [ [x[:] for x in tmp] ]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 100
        consts = ''
        coords = []
        coords1 = []

        for command in commands:
            #print command
            c = command['op']
            args = command['args']
            knob_value = 1

            if c == 'vary':
                knobName = command['knob']
                knob_value = frames[i][knobName]
            
            elif c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                        args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

        save_extension(screen, './anim/' + name + ('000' + str(i))[-3:])
            # end operation loop
    make_animation(name)
