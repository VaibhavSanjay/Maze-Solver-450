"""
    Minimal code for wall follower 
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSReliabilityPolicy
from rclpy.qos import QoSProfile
from sensor_msgs.msg import LaserScan

class Follow(Node):
    def __init__(self):
        super().__init__('follow')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        qos_profile = QoSProfile(depth=10)
        qos_profile.reliability = QoSReliabilityPolicy.BEST_EFFORT
        qos_profile.durability = QoSDurabilityPolicy.VOLATILE
        self.subscription= self.create_subscription(
            LaserScan,
            '/scan',  ## Read
            self.listener_callback,
            qos_profile,
        )
        timer_period = 0.2  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.state = -1

    def timer_callback(self):
        '''
        Publisher callback function
        TODO: implement
        '''
        msg = Twist()
        try:
            if self.state == 0:
                msg.linear.x = 0.2
                msg.angular.z = -0.3
            elif self.state == 1:
                msg.angular.z = 0.3
            elif self.state == 2:
                msg.linear.x = 0.5
        except KeyboardInterrupt:
            msg.linear.x = 0.0
        self.publisher_.publish(msg)
    
    def listener_callback(self,msg):
        '''
        Subscription Callback 
        TODO: implement
        '''
        regions = {
            'right':  min(min(msg.ranges[0:143]), 10),
            'fright': min(min(msg.ranges[144:287]), 10),
            'front':  min(min(msg.ranges[288:431]), 10),
            'fleft':  min(min(msg.ranges[432:575]), 10),
            'left':   min(min(msg.ranges[576:713]), 10),
        }

        d = 0.7
        front_d = 0.5

        if regions['front'] > front_d and regions['fleft'] > d and regions['fright'] > d:
            state_description = 'case 1 - nothing'
            self.state = 0
        elif regions['front'] < front_d and regions['fleft'] > d and regions['fright'] > d:
            state_description = 'case 2 - front'
            self.state = 1
        elif regions['front'] > front_d and regions['fleft'] > d and regions['fright'] < d:
            state_description = 'case 3 - fright'
            self.state = 2
        elif regions['front'] > front_d and regions['fleft'] < d and regions['fright'] > d:
            state_description = 'case 4 - fleft'
            self.state = 0
        elif regions['front'] < front_d and regions['fleft'] > d and regions['fright'] < d:
            state_description = 'case 5 - front and fright'
            self.state = 1
        elif regions['front'] < front_d and regions['fleft'] < d and regions['fright'] > d:
            state_description = 'case 6 - front and fleft'
            self.state = 1
        elif regions['front'] < front_d and regions['fleft'] < d and regions['fright'] < d:
            state_description = 'case 7 - front and fleft and fright'
            self.state = 1
        elif regions['front'] > front_d and regions['fleft'] < d and regions['fright'] < d:
            state_description = 'case 8 - fleft and fright'
            self.state = 0
        else:
            state_description = 'unknown case'

        self.get_logger().info(state_description)
        

def main(args=None):
    rclpy.init(args=args)
    my_follower = Follow()
    rclpy.spin(my_follower)
    my_follower.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
