# file settings - edit these to suit your application

# read file - temperature from one wire DS18B20 - used only on pi office clock
file_name = '/sys/bus/w1/devices/w1_bus_master1/28-041501ae5cff/w1_slave'

# for testing the application
test_file = '/home/pi/w1_slave'

# program logic uses the hostname to detect whether the host the application
# is running on is the right one.. if its not, the app uses the test file

host_name = 'apex-officeclock'

update_wait_time = 10

