/******************************************************************************
* @file    main.c
* @author  Rémi Pincent - INRIA
* @date    17/07/2018
*
* @brief Finite state machine C generated implementation from dia modeling tool
*
* Project : main file for fsm_example
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
#include <stdio.h>
#include"stdint.h"
#include "example_fsm.h"

/***************************************************************************
* Global Functions Definitions                                              
***************************************************************************/
int main(void)
{
    printf(" *** enter fsm state code generation example ***\n\n");
    example_fsm_init();
    /** this trigger must not cause any transition */
    example_fsm_update_on_trigger(ON_CONNECT);
    /** this trigger must not cause any transition */
    example_fsm_update_on_trigger(ON_DISCONNECT);
    for(uint8_t i = 0; i < 5; i++){
        /** this update won't call any action */
        example_fsm_update();
    }
    /** goes in DISCONNECT state */
    example_fsm_update_on_trigger(CONNECT_BTN_PRESSED);
    /** this update won't call any action */
    example_fsm_update();
    /** goes in CONNECT state */
    example_fsm_update_on_trigger(ON_CONNECT);
    for(uint8_t i = 0; i < 5; i++){
        /** call CONNECTED state action */
        example_fsm_update();
    }
    /** goes in DISCONNECT state */
    example_fsm_update_on_trigger(ON_DISCONNECT);
    /** this update won't call any action */
    example_fsm_update();
    /** this trigger must not cause any transition */
    example_fsm_update_on_trigger(CONNECT_BTN_PRESSED);
    /** this trigger must not cause any transition */
    example_fsm_update_on_trigger(ON_DISCONNECT);
    /** goes in CONNECT state */
    example_fsm_update_on_trigger(ON_CONNECT);
    /** call CONNECTED state action */
    example_fsm_update();
    /** goes in IDLE state */
    example_fsm_update_on_trigger(SERVER_UNREACHABLE);
    /** this update won't call any action */
    example_fsm_update();
    printf("\n *** exit fsm state code generation example ***\n\n");

    return 0;
}