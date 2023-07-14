
from manager import manager
from manager import message
from util import *
table_item = table_value(ip='172.18.36.131', port=12345, GPU_ID=0, GI_ID=3, MIG_config='2g.20gb')
destory_instance(table_item)
table_item = table_value(ip='172.18.36.131', port=12345, GPU_ID=0, GI_ID=4, MIG_config='2g.20gb')
destory_instance(table_item)

# test = manager(None, 12345)

# key = message('/home/zbw/MIG/schedule,Abacus,python test_program.py')
# value = config(ip='172.18.36.131', port=12345, GPU_ID=0, MIG_Instace='2g.20gb', Existence=True, MIG_UUID="MIG-e1a6d5d7-52af-5b1d-a897-ce0f71007d15")
# test.state_table()



# test.do_shecudle(key, value)

# value = config(ip='172.18.36.131', port=12345, GPU_ID=0, MIG_Instace='2g.20gb', Existence=True, MIG_UUID="MIG-47166aa1-8a66-5cba-a964-8dbcf1697934")

# test.do_shecudle(key, value)
