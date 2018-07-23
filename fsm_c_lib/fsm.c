/******************************************************************************
 * @file    fsm.c
 * @author  Rémi Pincent - INRIA
 * @date    01/03/2018
 *
 * @brief Finite state machine implementation
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

/**************************************************************************
 * Include Files
 **************************************************************************/
#include "fsm.h"

/**************************************************************************
 * Manifest Constants
 **************************************************************************/

/**************************************************************************
 * Type Definitions
 **************************************************************************/

/**************************************************************************
 * Global Variables
 **************************************************************************/

/**************************************************************************
 * Static Variables
 **************************************************************************/

/**************************************************************************
 * Macros
 **************************************************************************/

/**************************************************************************
 * Local Functions Declarations
 **************************************************************************/

/**************************************************************************
 * Global Functions Definitions
 **************************************************************************/
void fsm_update_on_trigger(FSMState *state, FSMTransition transitions[], uint16_t nb_transitions, FSMStateTrigger trigger)
{
    for(uint8_t i = 0; i < nb_transitions; i++)
    {
        if(state->id == transitions[i].curr_state.id
                && trigger == transitions[i].trigger
                && (!transitions[i].guard || transitions[i].guard()))
        {
            if(transitions[i].curr_state.action_on_state_exit)
            {
                transitions[i].curr_state.action_on_state_exit();
            }
            if(transitions[i].trans_action)
            {
                transitions[i].trans_action();
            }
            if(transitions[i].next_state.action_on_state_enter)
            {
                transitions[i].next_state.action_on_state_enter();
            }
            *state = transitions[i].next_state;
            break;
        }
    }
}

void fsm_update(FSMState state)
{
    if(state.action_on_state)
    {
        state.action_on_state();
    }
}

/**************************************************************************
 * Local Functions Definitions
 **************************************************************************/

