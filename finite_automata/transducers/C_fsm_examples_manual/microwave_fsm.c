#include <stdio.h>


typedef enum State {
    idle_closed,
    idle_open,
    cooking,
    cooking_completed,
    cooking_interrupted
} State;

const char* get_state_name(enum State state) {
   switch (state)
   {
      case idle_open: return "idle_open";
      case idle_closed: return "idle_closed";
      case cooking: return "cooking";
      case cooking_completed: return "cooking_completed";
      case cooking_interrupted: return "cooking_interrupted";
   }
}

enum Event {
    timeout,
    door_open,
    door_close,
    button_run,
    button_reset
};

const char* get_event_name(enum Event event) {
   switch (event)
   {
      case timeout: return "timeout";
      case door_open: return "door_open";
      case door_close: return "door_close";
      case button_run: return "button_run";
      case button_reset: return "button_reset";
   }
}

enum Instr {
    timer_set,
    timer_add,
    timer_pause,
    timer_resume,
    magnetron_off,
    magnetron_on,
    lamp_off,
    lamp_on,
    beeping_off,
    beeping_on
};

const char* get_instr_name(enum Instr instr) {
   switch (instr)
   {
      case timer_set: return "timer_set";
      case timer_add: return "timer_add";
      case timer_pause: return "timer_pause";
      case timer_resume: return "timer_resume";
      case magnetron_on: return "magnetron_on";
      case magnetron_off: return "magnetron_off";
      case lamp_on: return "lamp_on";
      case lamp_off: return "lamp_off";
      case beeping_on: return "beeping_on";
      case beeping_off: return "beeping_off";
   }
}

void send_instruction(enum Instr instr, int param) {
    printf("\nInstruction sent: %s, %d", get_instr_name(instr), param);
}

char* get_next_event() {
    enum Event evt;
    scanf("%d", &evt);
    printf("Event: %s", get_event_name(evt));
}


int main() {
    enum State state = idle_closed;
    send_instruction(Instr.power_off, 0);
    send_instruction(Instr.lamp_off, 0);
    send_instruction(Instr.beeping_off, 0);
    while (1) {
        event = get_next_event();

        switch (state) {
            case (idle_closed): {
                switch (event) {
                    case (door_open) {
                        send_instruction(Instr.lamp_on, 0);
                        state = State.door_open;
                        break;
                    }
                    case (button_run) {
                        send_instruction(Instr.timer_set, 30);
                        send_instruction(Instr.lamp_on, 0);
                        send_instruction(Instr.magnetron_on, 0);
                        state = State.cooking;
                        break;
                    }
                }
            }

            case (idle_open) {
                switch (event) {
                    case (door_close) {
                        send_instruction(Instr.lamp_off, 0);
                        state = State.idle_closed;
                        break;
                    }
                }
            }

            case (cooking) {
                switch (event) {
                    case (button_reset) {
                        send_instruction(Instr.timer_set, 0);
                        send_instruction(Instr.lamp_off, 0);
                        send_instruction(Instr.magnetron_off, 0);
                        state = State.idle_closed;
                        break;
                    }
                    case (button_run) {
                        send_instruction(Instr.timer_add, 30);
                        state = State.cooking;
                        break;
                    }
                    case (door_open) {
                        send_instruction(Instr.timer_pause, 0);
                        send_instruction(Instr.magnetron_off, 0);
                        state = State.cooking_interrupted;
                        break;
                    }
                    case (timeout) {
                        send_instruction(Instr.beeping_on, 0);
                        send_instruction(Instr.magnetron_off, 0);
                        state = State.cooking_completed;
                        break;
                    }
                }
            }

            case (cooking_interrupted) {
                switch (event) {
                    case (door_close) {
                        send_instruction(Instr.timer_resume, 0);
                        send_instruction(Instr.magnetron_on, 0);
                        state = State.cooking;
                        break;
                    }
                    case (button_reset) {
                        send_instruction(Instr.timer_set, 0);
                        state = State.idle_open;
                        break;
                    }
                    case (button_run) {
                        send_instruction(Instr.timer_add, 30);
                        state = State.cooking_interrupted;
                        break;
                    }
                }
            }

            case (cooking_completed) {
                switch (event) {
                    case (door_open) {
                        send_instruction(Instr.beeping_off, 0);
                        state = State.idle_open;
                        break;
                    }
                    case (button_reset) {
                        send_instruction(Instr.lamp_off, 0);
                        send_instruction(Instr.beeping_off, 0);
                        state = State.idle_closed;
                        break;
                    }
                    case (button_run) {
                        send_instruction(Instr.magnetron_on, 0);
                        send_instruction(Instr.beeping_off, 0);
                        send_instruction(Instr.timer_set, 30);
                        state = State.cooking;
                        break;
                    }
                }
            }
        }
    }
}