/******************************************************************************
 * @file    fsm
 * @author  Rémi Pincent - INRIA
 * @date    12/07/2018
 *
 * @brief Finite state machine declarations
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
#ifndef FSM_H
#define FSM_H

#ifdef __cplusplus
extern "C"
{
#endif
/**************************************************************************
 * Include Files
 **************************************************************************/
#include <stdint.h>
#include <stdbool.h>
/**************************************************************************
 * Manifest Constants
 **************************************************************************/

/**************************************************************************
 * Type Definitions
 **************************************************************************/
typedef bool (*Guard)(void);
typedef void (*TransitionAction)(void);
typedef void (*ActionOnStateEnter)(void);
typedef void (*ActionOnStateExit)(void);
typedef void (*ActionOnState)(void);
typedef uint16_t FSMStateId;
typedef uint16_t FSMStateTrigger;

typedef struct
{
    FSMStateId id;
    ActionOnStateEnter action_on_state_enter;
    ActionOnStateExit action_on_state_exit;
    ActionOnState action_on_state;
}FSMState;

typedef struct
{
    FSMState curr_state;
    FSMState next_state;
    FSMStateTrigger trigger;
    Guard guard;
    TransitionAction trans_action;
}FSMTransition;

/**************************************************************************
 * Global variables
 **************************************************************************/

/**************************************************************************
 * Macros
 **************************************************************************/

/**************************************************************************
 * Global Functions Declarations
 **************************************************************************/
/**
 * Update FSM on given trigger
 * @param state
 * @param transitions
 * @param nb_transitions
 * @param trigger
 */
void fsm_update_fsm_on_trigger(FSMState *state, FSMTransition transitions[], uint16_t nb_transitions, FSMStateTrigger trigger);

/**
 * Update FSM in given state i.e. runs state "do action"
 * @param state
 */
void fsm_update_fsm(FSMState state);

#ifdef __cplusplus
}
#endif

#endif /* FSM_H */
