from ursina import *
from direct.actor.Actor import Actor
import random


app = Ursina()
window.borderless = True
window.fps_counter.enabled = False

world = Entity()
player = Entity(model='cube', color=color.clear, scale=(3, 3, 3), position=(-50, 50, 70), collider='box')
actor = Actor('moose.glb')
actor.reparent_to(player)
actor.loop('walk')
actor.setPos(0, 1, 0)
actor.setPlayRate(2, 'walk')

fly = Entity(model='cube', position=(300, 200, -300))

terrain = Entity(model='mooseislandobj/mooseisland', parent=world, texture='textures/grass', collider='mesh',)  # Adjust y position
water = Entity(model='mooseislandobj/water', parent=world, texture='textures/water', collider='mesh')
waterfall_sound = Entity(model='sphere', scale=(1, 1, 1), color=color.green)
waterfall_cube = Entity(model='cube', scale=(30, 100, 50), position=(20, 5, 0), collider='box', color=color.clear)

rocks = Entity(model='mooseislandobj/rocks', parent=world, color=color.gray, collider='mesh')
trees = Entity(model='mooseislandobj/trees', texture='textures/wood', collider='mesh')
# leaves = Entity(model='mooseislandobj/leaves', color=color.green, collider='mesh')
camera1 = Entity(model='sphere', color=color.clear, position=(-117, 20, 110), rotation_y=120)
cam1_box = Entity(model='cameras/cam1_box', color=color.clear, collider='box')
camera2 = Entity(model='sphere', color=color.clear, position=(-120, 20, -120), rotation_y=60)
cam2_box = Entity(model='cameras/cam2_box', color=color.clear, collider='box')
food = Entity(model='sphere', scale=(2,2,2), color=color.red, position=(random.uniform(-200, 200), 100, random.uniform(-200, 200)), collider='sphere')
food_box = Entity(model='wireframe_cube', color=color.clear, scale=(10, 10, 10), collider='box' )

# Create an Audio object and load a sound file
sound = Audio('waterfall.mp3', loop=True, autoplay=True)
river_sound = Audio('river.mp3', loop=True, autoplay=True, volume=.5)

initial_player_position = (-0, 50, 0)
# food_reset_position = (random.uniform(-50, 50), 30, random.uniform(-50, 50))

sky = Sky(texture='sky_sunset')



# Player properties
player.velocity = Vec3(0, 0, 0)
food.velocity = Vec3(0, 0, 0)


speed = 10
r_speed = 50

# Day/Night cycle parameters
day_duration = 20  # in seconds
current_time = 0
is_daytime = True  # Flag to track day/night state

direction = None
movement_duration = 1.0
remaining_duration = 0.0

# energy bar !
max_energy = 100
current_energy = max_energy
energy_depletion_rate = 5
energy_recharge_amount = 40
ui_bar = Entity(scale=(0.2, 0.2), parent=camera.ui)
ui_bar.x = -.6
ui_bar.y = -.35
energy_bar = Entity(model='quad', scale=(current_energy / max_energy, 0.1), color=color.green, origin=(-.5, 0), parent=ui_bar)
energy_text = Text('Energy', scale=(1, 1), position=(-.6, -.3), parent=camera.ui)

eating_duration = 100
eating_rate = 10
current_eating_duration = eating_duration
is_eating = False
max_eating_duration = 100

# Level properties
current_level = 0
level_text = Text(text=f'Food eaten: {current_level}', scale=(2.5, 2.5))
parent = camera.ui
# Move the text to a specific position on the screen
level_text.x = -.6  # Adjust the x-coordinate as needed
level_text.y = .35  # Adjust the y-coordinate as needed

def start_movement():
    global direction, remaining_duration
    direction = random.choice(['w', 'a', 's', 'd', 'z', 'x'])
    remaining_duration = movement_duration

def update_energy_bar():
    energy_bar.scale = (current_energy * 2 / max_energy, 0.1)

def move_towards_target(target_position):
    direction = target_position - player.position
    direction.y = 0  # Optional: Keep the movement in the xz-plane
    direction = direction.normalized()

    # Restrict movement to four directions
    if abs(direction.x) > abs(direction.z):
        direction.z = 0
    else:
        direction.x = 0

    player.x += direction.x * speed * time.dt
    player.z += direction.z * speed * time.dt

def big_fly():
    fly_start_position = (-300, 300, -300)
    fly_target =(300, 150, 300)
    is_attached = False

    # Check if the 'o' key is held down
    if held_keys['o'] and not is_attached:
        # Move the fly towards the player position using lerp
        fly.position = lerp(fly.position, player.position, time.dt * 2)

        # Check if the fly is close to the player's position
        if distance(fly.position, player.position) < 10:
            # Attach the player to the fly
            is_attached = True

    # If attached, move both the fly and player towards the target position
    if is_attached:
        player.position = lerp(player.position, fly_target, time.dt * .5)
        fly.position = lerp(fly.position, fly_target, time.dt * .5)
# Check if the distance between the fly and the target is small
        if distance(fly.position, fly_target) < 100:
            # Detach the player and reset the is_attached flag
            is_attached = False

            # Move the fly back to the start position
            fly.position = fly_start_position




def update():

    # Calculate the distance between the player and the sound_entity
    distance = (player.position - waterfall_sound.position).length()

    # Map the distance to a volume range (adjust these values as needed)
    max_distance = 200.0
    min_volume = 0.05
    max_volume = 1.0
    volume = lerp(min_volume, max_volume, 1 - min(distance, max_distance) / max_distance)

    # Set the volume of the sound
    sound.volume = volume

    gravity = -9  # Adjust the gravity strength as needed
    food_gravity = -1
    camera.fov = 50
    global current_time, is_daytime, remaining_duration, current_energy, direction, current_eating_duration, is_eating, current_level

    food_reset_position = (random.uniform(-200, 200), 150, random.uniform(-200, 200))

    current_energy -= energy_depletion_rate * time.dt
    update_energy_bar()

    big_fly()

    # Increment the time
    current_time += time.dt

    # Calculate the interpolation factor (0 to 1) based on the current time
    t = current_time / day_duration

    # Interpolate between day and night colors based on the day/night state
    day_color = color.rgb(135, 206, 250)  # Light blue for day
    night_color = color.rgb(0, 0, 128)  # Dark blue for night
    interpolated_color = lerp(day_color, night_color, t) if is_daytime else lerp(night_color, day_color, t)

    # Interpolate between day and night ambient light colors
    day_ambient_color = color.rgb(230, 230, 230)
    night_ambient_color = color.rgb(100, 150, 160)
    interpolated_ambient_color = lerp(day_ambient_color, night_ambient_color, t) if is_daytime else lerp(night_ambient_color, day_ambient_color, t)


    # Update the sky color
    sky.color = interpolated_color

    # Update ambient light color
    ambient_light.color = interpolated_ambient_color

    # Check if a full cycle is completed
    if current_time >= day_duration:
        current_time = 0  # Reset current_time for the new cycle
        is_daytime = not is_daytime  # Toggle day/night state
    


    # Apply gravity
    player.velocity.y += gravity * time.dt
    food.velocity.y += food_gravity * time.dt

    # Update player position based on velocity
    player.y += player.velocity.y * time.dt
    food.y += food.velocity.y * time.dt

    # Player movement controls
    move_direction = Vec3(0, 0, 0)
    # if held_keys['k']:
    #     move_towards_target(food.position)

    if current_energy <= 10:
        direction = 'x'
        move_direction.x += 0 * time.dt  # Optional: stop movement when energy is 0
        current_energy += energy_recharge_amount * time.dt
        actor.play('sleep')
        actor.setPos(0, 0, 0)
    if current_energy > max_energy:
        current_energy = max_energy
    else:
        if remaining_duration <= 0:
            actor.loop('walk')
            actor.setPos(0, 1, 0)
            start_movement()


    if direction == 'w':
        move_direction.z += 1 * time.dt
        player.rotation_y = 90
    elif direction == 's':
        move_direction.z -= 1 * time.dt
        player.rotation_y = 270
    elif direction == 'a':
        move_direction.x -= 1 * time.dt
        player.rotation_y = 0
    elif direction == 'd':
        move_direction.x += 1 * time.dt
        player.rotation_y = 180
    elif direction == 'z':
        move_direction.x += 0 * time.dt
    elif direction == 'x':
        move_direction.x += 0 * time.dt
        current_energy += energy_recharge_amount * time.dt
        actor.play('sleep')
        actor.setPos(0, 0, 0)
        if current_energy > max_energy:
            current_energy = max_energy
    if current_energy >= 70 and food.intersects(terrain):
         move_towards_target(food.position)

     # Make the player entity turn in the direction of movement
    # if move_direction.length() > 0:
    #     player.look_at(player.position + move_direction)
    

    remaining_duration -= time.dt


    # Normalize the direction vector to ensure consistent movement speed in all directions
    move_direction = move_direction.normalized()

    # Check if the player is about to collide with a wall in the moving direction
    hit_info = raycast(player.position, direction=move_direction, distance=1, ignore=[player, cam1_box, cam2_box, food_box])

    if not hit_info.hit:
        # Update player position if there's no collision
        player.x += move_direction.x * speed * time.dt
        player.z += move_direction.z * speed * time.dt


    # Check if the player is on the terrain collider
    hit_info = raycast(player.position, direction=(0, -1, 0), distance=1, ignore=[player, cam1_box, cam2_box, food_box])

    if hit_info.hit:
        player.y = hit_info.world_point.y + 1  # Adjust 1 to the player's height
        player.velocity.y = 0  # Reset vertical velocity when on the ground

    if player.intersects(cam1_box).hit:
        camera.position = camera1.position
        camera.rotation = camera1.rotation
        camera.fov = 100
    elif player.intersects(cam2_box).hit:
        camera.position = camera2.position
        camera.rotation = camera2.rotation
        camera.fov = 100
    else:
        camera.position = player.position + (-30, 10, 0)
        camera.rotation = (0, 90, 0)
        camera.fov = 100

    if player.y < -10:
        player.position = initial_player_position

    
    if food.intersects(terrain):
        food_gravity = 10
        food.velocity.y = 0
    elif food.intersects(water).hit:
        food.position = food_reset_position
    elif food.y < -20:
        food.position = food_reset_position

    food_box.position = food.position

    if player.intersects(food_box).hit:
        current_eating_duration -= eating_rate * time.dt
        is_eating = True
        if current_eating_duration <= 0:
            food.position = food_reset_position
            is_eating = False
            current_eating_duration = max_eating_duration
            current_level += 1
            level_text.text = f'Food eaten: {current_level}'

    else:
        is_eating = False

    if is_eating:
        direction = 'z'


# Ambient light
ambient_light = AmbientLight(color=color.rgb(100, 100, 100), intensity=0.5)


app.run()
