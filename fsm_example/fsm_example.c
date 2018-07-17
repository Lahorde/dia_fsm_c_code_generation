/******************************************************************************
* @file    fsm
* @author  Rémi Pincent - INRIA
* @date    17/07/2018
*
* @brief Finite state machine C generated implementation from dia modeling tool
*
* Project : fsm
* Contact:  Rémi Pincent - remi.pincent@inria.fr
*
* Revision History:
* Insert github reference
* 
* LICENSE :
* fsm (c) by Rémi Pincent
* fsm is licensed under a
* Creative Commons Attribution-NonCommercial 3.0 Unported License.
*
* You should have received a copy of the license along with this
* work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.
*****************************************************************************/
/***************************************************************************
* Include Files/
***************************************************************************/

/** USER CODE BEGIN Includes */
#include <stdio.h>
/** USER CODE END Includes */
/***************************************************************************
* Manifest Constants                                                        
***************************************************************************/

/** USER CODE BEGIN Consts */
/** USER CODE END Consts */
/***************************************************************************
* Type Definitions                                                          
***************************************************************************/

/** USER CODE BEGIN Types */
/** USER CODE END Types */
/***************************************************************************
* Local Functions Declarations                                              
***************************************************************************/

/** USER CODE BEGIN User Local Functions Declarations */
static void show_msg(char *);
static void prepare_connection(void);
static void poll_server(void);
static bool is_connection_speed_ok(void);
static bool is_server_ready(void);
static bool is_locked(void);

/** USER CODE END User Local Functions Declarations */
/***************************************************************************
* Static Variables                                                          
***************************************************************************/

/** USER CODE BEGIN User Static Variables Declarations */
/** USER CODE END User Static Variables Declarations */
/***************************************************************************
* Global Functions Definitions                                              
***************************************************************************/
/** USER CODE BEGIN User Global Functions Definitions */
int main(void)
{
    show_msg(" *** enter fsm state code generation example ***\n");
    init_fsm();
    /** this trigger must not cause any transition */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, ON_CONNECT);
    /** this trigger must not cause any transition */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, ON_DISCONNECT);
    for(uint8_t i = 0; i < 5; i++){
        /** this update won't call any action */
        fsm_update_fsm(state);
    }
    /** goes in DISCONNECT state */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, CONNECT_BTN_PRESSED);
    /** this update won't call any action */
    fsm_update_fsm(state);
    /** goes in CONNECT state */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, ON_CONNECT);
    for(uint8_t i = 0; i < 5; i++){
        /** call CONNECTED state action */
        fsm_update_fsm(state);
    }
    /** goes in DISCONNECT state */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, ON_DISCONNECT);
    /** this update won't call any action */
    fsm_update_fsm(state);
    /** this trigger must not cause any transition */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, CONNECT_BTN_PRESSED);
    /** this trigger must not cause any transition */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, ON_DISCONNECT);
    /** goes in CONNECT state */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, ON_CONNECT);
    /** call CONNECTED state action */
    fsm_update_fsm(state);
    /** goes in IDLE state */
    fsm_update_fsm_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, SERVER_UNREACHABLE);
    /** this update won't call any action */
    fsm_update_fsm(state);
    show_msg("\n *** exit fsm state code generation example ***\n");
    return 0;
}
/** USER CODE END User Global Functions Definitions */

/***************************************************************************
* Local Functions Definitions                                               
***************************************************************************/
/** USER CODE BEGIN User Static Functions Definitions */
void show_msg(char *msg)
{
    printf("%s\n", msg);
}

void prepare_connection(void)
{
    show_msg("preparing_connecton");
}

void poll_server(void)
{
    show_msg("polling server");
}

bool is_connection_speed_ok(void)
{
    show_msg("is_connection_speed_ok() called");
    return true;
}

bool is_server_ready(void)
{
    show_msg("is_server_ready() called");
    return true;
}

bool is_locked(void)
{
    show_msg("is_locked() called");
    return false;
}
/** USER CODE END User Static Functions Definitions */
