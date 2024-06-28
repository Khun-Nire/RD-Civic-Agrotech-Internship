import serial
import time

from Height_detection import green_Detection

file_path = 'EEPROM_psudo.txt'
comPort = 'COM3'
Layer_totals = 5

Serial = serial.Serial(port=comPort, baudrate=115200, timeout=0.1)

def Read_lamp_distance(Layer):
    with open(file_path, 'r') as file:#เปิดไฟล์ที่เก็บความสูงของชั้นปลูกพืชแต่ละชั้น
        lines = file.readlines()#อ่านตัวเลขแต่ละบรรทัด แต่ละบรรทัดแทนชั้นของชั้นปลูก
    return lines[Layer - 1]

def Backup_lamp_distance(Layer, Replace_value):#อัพเดทค่าตำแหน่งที่โคมไฟเลื่อนไปอยู่เสมอ
    # Read the content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Replace the specific line
    lines[Layer - 1] = str(Replace_value) + '\n'  # Adjust index since list is 0-indexed

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)

def MotorControl(Text_serial):
    Text_hex_list = Text_serial.split(" ")
    Hex_list = [int(x, 16) for x in Text_hex_list]
    if Text_hex_list[0] == "BA":
        if Text_hex_list[2] == "6C":
            Current_height = int(Read_lamp_distance(Hex_list[1])) - Hex_list[3]
        elif Text_hex_list[2] == "72":
            Current_height = int(Read_lamp_distance(Hex_list[1])) + Hex_list[3]

        time_to_move = int(abs(Hex_list[3])/8)

        if Current_height < 0:
            Current_height = 0
        Backup_lamp_distance(Hex_list[1], Current_height)
        Serial.write(bytes(Hex_list))
        print("The lamp is adjusting its height, please wait...")
        time.sleep(time_to_move)#รอลิฟเคลื่อนที่ไปที่ชั้นถัดไป
        print("The lamp stop at: ", Hex_list[3])
    elif Text_hex_list[0] == "6C":
        Current_layer = int(Read_lamp_distance(6))
        Backup_lamp_distance(6, Hex_list[1])
        Serial.write(bytes(Hex_list))
        print("Elevator in motion, please wait...")
        time.sleep(13*abs(Current_layer-Hex_list[1]))#รอลิฟเคลื่อนที่ไปที่ชั้นถัดไป
        print("The Elevator stop at: ", Hex_list[1])
    elif Text_hex_list[0] == "4D":
        Serial.write(bytes(Hex_list))
        print("Elevator in motion, please wait...")
        time.sleep(6)#รอลิฟเคลื่อนที่ไปที่ชั้นถัดไป
        print("Warnted! The Elevator stop in half step")
    else:
        Serial.write(bytes(Hex_list))

    print("Write Serial: ",Hex_list)
    print("_End_MotorControl_______________________________________")

""" 
def Serial_Reading():
    Height = []

    while True:
        time.sleep(1)
        if Serial.in_waiting > 0:
            SerialRead = Serial.read(Serial.in_waiting)
            print("serialRead: ", SerialRead)

            decodeRead = SerialRead.decode('latin-1')
            print("decodeRead: ", decodeRead)

            Height = re.findall(r'\d+', decodeRead)
            print("Height: ", Height)
        else:
            if len(Height) > 1:
                print("_End_sub_function_______________________________________")
                return float(Height[-2])
            else:
                return 0
"""

def Reset_moving_lamp(Layer):
    lamp_distance = int(Read_lamp_distance(Layer))
    time_to_wait = int(int(Read_lamp_distance(Layer))/16)
    
    if time_to_wait > 0:
        MotorControl("BA "+format(Layer, '02X')+" 6C "+ format(lamp_distance, '02X') +" FF FF FF")#เปลี่ยนเลขฐาน 16 ที่เป็น String เป็น int
        time.sleep(1 + 2*time_to_wait)
        print("Stop at: -", format(lamp_distance, '02X'))

try:
    while True:
        user_input = input("fiveHex: ")

        if user_input == "exit":
            print("exit")
            break
        elif user_input == "auto":
            for i in range(0,5):#Set Zero for lamp's distance for 5 layers
                Reset_moving_lamp(i+1)
            Offset_direction = input("Offset (cm): ")#Setting your desire distance between lamp and tree

            if Offset_direction == "exit":
                break

            for i in range(0,Layer_totals):
                print("Layer: ",i+1)
                
                MotorControl("6C "+format(i+1, '02X')+" FF FF FF")
                MotorControl("4D 72 20 4E 00 FF FF FF")
                time.sleep(5)#delay for waiting a shaking camera
                Count = 0

                while Count < 3:
                    time.sleep(0.1)
                    Green_tree_Detection_List = green_Detection()
                    if Green_tree_Detection_List:
                        Percentage_of_Green = Green_tree_Detection_List[0]
                        Move_Lamp_to = float(Green_tree_Detection_List[1]-int(Offset_direction))
        
                        if Percentage_of_Green > 0:
                            print("Percentage of Green pass: ", Percentage_of_Green)

                            if Move_Lamp_to < 0:
                                Move_Lamp_to = 0
                            elif Move_Lamp_to < 1:
                                Move_Lamp_to *= 10.67
                            elif Move_Lamp_to < 4:
                                Move_Lamp_to *= 9.143
                            elif Move_Lamp_to < 7:
                                Move_Lamp_to *= 7.164
                            elif Move_Lamp_to < 10:
                                Move_Lamp_to *= 6.809
                            else:
                                Move_Lamp_to *= 6.557

                            Last_hex = format(int(Move_Lamp_to), '02X')
                            MotorControl("BA "+format(5-i, '02X')+" 72 "+Last_hex+" 10 FF FF FF")
                            print("Move Lamp to (cm), (hex): ",str(Move_Lamp_to), Last_hex)
                            break
                        else:
                            print("Percentage of Green too low: ", Percentage_of_Green)
                    Count += 1
                if Count == 3:
                    print("_Time_out_please_try_again_______________________________________")

                MotorControl("4D 6C 20 4E 00 FF FF FF")

            MotorControl("6C 01 FF FF FF")
            print("_auto_Done_______________________________________")

        elif user_input == "lift":
            step = int(input("step: "))
            Up_or_down = int(input("Up(1) Down(0): "))
            if Up_or_down == 1:
                for i in range(0, step):
                    MotorControl("4D 6C D0 07 00 FF FF FF")
                    time.sleep(1)
            elif Up_or_down == 0:
                for i in range(0, step):
                    MotorControl("4D 72 D0 07 00 FF FF FF")
                    time.sleep(1)
        else:
            MotorControl(user_input)
            for i in range(0,5):
                print("Layer"+str(i)+": "+Read_lamp_distance(i))
            print("_End_Direct_Command_______________________________________")
        print("_Program_Done_______________________________________")

finally:
    Serial.close()