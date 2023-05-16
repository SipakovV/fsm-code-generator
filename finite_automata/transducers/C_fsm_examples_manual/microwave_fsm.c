#include <stdio.h>

/*
// State constants
#define STATE_IDLE_CLOSED 100
#define STATE_IDLE_OPEN 101
#define STATE_COOKING 102
#define STATE_COOKING_COMPLETED 103
#define STATE_COOKING_INTERRUPTED 104

// Event constants
#define EVENT_TIMEOUT 200
#define EVENT_DOOR_CLOSE 201
#define EVENT_DOOR_OPEN 202
#define EVENT_BUTTON_RUN 203
#define EVENT_BUTTON_RESET 204

// Instruction constants
#define INSTR_TIMER_SET 300
#define INSTR_TIMER_ADD 301
#define INSTR_TIMER_PAUSE 302
#define INSTR_TIMER_RESUME 303
*/


enum State {
    state_idle_closed,
    state_idle_open,
    state_cooking,
    state_cooking_completed,
    state_cooking_interrupted
};
enum Event {
    event_timeout,
    event_door_open,
    event_door_close,
    event_button_run,
    event_button_reset
};
enum Instr {
    instr_timer_set,
    instr_timer_add,
    instr_timer_pause,
    instr_timer_resume,
    instr_magnetron_off,
    instr_magnetron_on,
    instr_lamp_off,
    instr_lamp_on,
    instr_beeping_off,
    instr_beeping_on
};


const char* get_state_name(enum State state) {
   switch (state)
   {
      case state_idle_open: return "idle_open";
      case state_idle_closed: return "idle_closed";
      case state_cooking: return "cooking";
      case state_cooking_completed: return "cooking_completed";
      case state_cooking_interrupted: return "cooking_interrupted";
   }
}



const char* get_event_name(enum Event event) {
   switch (event)
   {
      case event_timeout: return "timeout";
      case event_door_open: return "door_open";
      case event_door_close: return "door_close";
      case event_button_run: return "button_run";
      case event_button_reset: return "button_reset";
      default: return "unknown event";
   }
}


const char* get_instr_name(enum Instr instr) {
   switch (instr)
   {
      case instr_timer_set: return "timer_set";
      case instr_timer_add: return "timer_add";
      case instr_timer_pause: return "timer_pause";
      case instr_timer_resume: return "timer_resume";
      case instr_magnetron_on: return "magnetron_on";
      case instr_magnetron_off: return "magnetron_off";
      case instr_lamp_on: return "lamp_on";
      case instr_lamp_off: return "lamp_off";
      case instr_beeping_on: return "beeping_on";
      case instr_beeping_off: return "beeping_off";
   }
}


void send_instruction(enum Instr instr, int param) {
    printf("Instruction sent: %s, %d\n", get_instr_name(instr), param);
}

enum Event get_next_event() {
    enum Event evt;
    scanf("%d", &evt);
    printf("Event: %s\n", get_event_name(evt));
    return evt;
}


void run_fsm() {
    enum State state = state_idle_closed;
    enum Event event;

    printf("Available events:\n");
    for (int i = event_timeout; i <= event_button_reset; i++) {
        printf("%d: %s\n", i, get_event_name(i));
    }
    send_instruction(instr_magnetron_off, 0);
    send_instruction(instr_lamp_off, 0);
    send_instruction(instr_beeping_off, 0);
    while (1) {
        printf("State: %s\n", get_state_name(state));
        event = get_next_event();

        switch (state) {
            case (state_idle_closed): {
                switch (event) {
                    case (event_door_open): {
                        send_instruction(instr_lamp_on, 0);
                        state = state_idle_open;
                        break;
                    }
                    case (event_button_run): {
                        send_instruction(instr_timer_set, 30);
                        send_instruction(instr_lamp_on, 0);
                        send_instruction(instr_magnetron_on, 0);
                        state = state_cooking;
                        break;
                    }
                }
                break;
            }

            case (state_idle_open): {
                switch (event) {
                    case (event_door_close): {
                        send_instruction(instr_lamp_off, 0);
                        state = state_idle_closed;
                        break;
                    }
                }
                break;
            }

            case (state_cooking): {
                switch (event) {
                    case (event_button_reset): {
                        send_instruction(instr_timer_set, 0);
                        send_instruction(instr_lamp_off, 0);
                        send_instruction(instr_magnetron_off, 0);
                        state = state_idle_closed;
                        break;
                    }
                    case (event_button_run): {
                        send_instruction(instr_timer_add, 30);
                        state = state_cooking;
                        break;
                    }
                    case (event_door_open): {
                        send_instruction(instr_timer_pause, 0);
                        send_instruction(instr_magnetron_off, 0);
                        state = state_cooking_interrupted;
                        break;
                    }
                    case (event_timeout): {
                        send_instruction(instr_beeping_on, 0);
                        send_instruction(instr_magnetron_off, 0);
                        state = state_cooking_completed;
                        break;
                    }
                }
                break;
            }

            case (state_cooking_interrupted): {
                switch (event) {
                    case (event_door_close): {
                        send_instruction(instr_timer_resume, 0);
                        send_instruction(instr_magnetron_on, 0);
                        state = state_cooking;
                        break;
                    }
                    case (event_button_reset): {
                        send_instruction(instr_timer_set, 0);
                        state = state_idle_open;
                        break;
                    }
                    case (event_button_run): {
                        send_instruction(instr_timer_add, 30);
                        state = state_cooking_interrupted;
                        break;
                    }
                }
                break;
            }

            case (state_cooking_completed): {
                switch (event) {
                    case (event_door_open): {
                        send_instruction(instr_beeping_off, 0);
                        state = state_idle_open;
                        break;
                    }
                    case (event_button_reset): {
                        send_instruction(instr_lamp_off, 0);
                        send_instruction(instr_beeping_off, 0);
                        state = state_idle_closed;
                        break;
                    }
                    case (event_button_run): {
                        send_instruction(instr_magnetron_on, 0);
                        send_instruction(instr_beeping_off, 0);
                        send_instruction(instr_timer_set, 30);
                        state = state_cooking;
                        break;
                    }
                }
                break;
            }
        }
    }
}

int main() {
    run_fsm();
}