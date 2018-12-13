REBOL []

outport: open/lines tcp://localhost:13857
on: 1
off: 0

pl0:  "[(100,200, 0), (100,300, 65280), (200,300, 65280), (200,200, 65280), (100,200, 65280)]"


oscommand: to-string reduce ["pl/0 " pl0]    
insert outport oscommand
    
for counter 1 2 1 [
    ;;  print counter
    oscommand: to-string reduce ["/40h/clear " on]    
    insert outport oscommand
    wait 0.3

]

for counter 1 2 1 [
    for raw 0 7 1 [
        oscommand: to-string reduce ["/40h/led_row " raw " " on]  
        insert outport oscommand
        wait 0.001
        ]

]

for counter 1 2 1 [
    ;;  print counter
    oscommand: to-string reduce ["/40h/frame 0 126 126 126 126 126 126 0"]    
    insert outport oscommand
            
    wait 0.3
    
]

close outport