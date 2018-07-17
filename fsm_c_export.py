# -*- coding: utf-8 -*-
'''
@file    fsm_c_export.py 
@author  Rémi Pincent - INRIA
@date    17/08/2018

 @brief C code generation for Dia Finite State Machines

 Project : fsm 
 Contact:  Rémi Pincent - remi.pincent@inria.fr

 Revision History:

  LICENSE :
      fsm (c) by Rémi Pincent
      fsm is licensed under a
      Creative Commons Attribution-NonCommercial 3.0 Unported License.

  You should have received a copy of the license along with this
  work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.
'''
import dia
import uml_stm_export
from datetime import datetime

class CFSMExporter(uml_stm_export.SimpleSTM):
    now = datetime.now()

    USER_CODE_BEGIN = "USER CODE BEGIN"
    USER_CODE_END = "USER CODE END"

    CODE_PREAMBLE = \
        "/******************************************************************************\n" + \
        "* @file    fsm_example.c\n"                                                        + \
        "* @author  Rémi Pincent - INRIA\n"                                                 + \
        "* @date    {}\n".format(datetime.now().strftime('%d/%m/%Y'))                       + \
        "*\n"                                                                               + \
        "* @brief Finite state machine C generated implementation from dia modeling tool\n" + \
        "*\n"                                                                               + \
        "* Project : fsm\n"                                                                 + \
        "* Contact:  Rémi Pincent - remi.pincent@inria.fr\n"                                + \
        "*\n"                                                                               + \
        "* Revision History:\n"                                                             + \
        "* Insert github reference\n"                                                       + \
        "* \n"                                                                              + \
        "* LICENSE :\n"                                                                     + \
        "* fsm (c) by Rémi Pincent\n"                                                       + \
        "* fsm is licensed under a\n"                                                       + \
        "* Creative Commons Attribution-NonCommercial 3.0 Unported License.\n"              + \
        "*\n"                                                                               + \
        "* You should have received a copy of the license along with this\n"                + \
        "* work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.\n"          + \
        "*****************************************************************************/\n"  + \
        "/***************************************************************************\n"    + \
        "* Include Files/\n"                                                                + \
        "***************************************************************************/\n"    + \
        "#include \"fsm.h\"\n\n"

    CONST_DEFS = \
        "/***************************************************************************\n" + \
        "* Manifest Constants                                                        \n" + \
        "***************************************************************************/\n"

    TYPE_DEFS = \
        "/***************************************************************************\n" + \
        "* Type Definitions                                                          \n" + \
        "***************************************************************************/\n"

    STATIC_VARS = \
        "/***************************************************************************\n" + \
        "* Static Variables                                                          \n" + \
        "***************************************************************************/\n"

    STATIC_FUNCS_DECLS = \
        "/***************************************************************************\n" + \
        "* Local Functions Declarations                                              \n" + \
        "***************************************************************************/\n"
    
    GLOBAL_FUNCS_DEFS = \
        "/***************************************************************************\n" + \
        "* Global Functions Definitions                                              \n" + \
        "***************************************************************************/\n"

    STATIC_FUNCS_DEFS = \
        "/***************************************************************************\n" + \
        "* Local Functions Definitions                                               \n" + \
        "***************************************************************************/\n"

    FSM_ACTIONS_DEFS = \
        "/**************\n" + \
        "* FSM actions  \n" + \
        "**************/\n"        

    FSM_GUARDS_DEFS = \
        "/**************\n" + \
        "* FSM guards  \n" + \
        "**************/\n"   

    def __init__(self):
        uml_stm_export.SimpleSTM.__init__(self)
        self.filename = ""

    def begin_render (self, data, filename):
        self.filename = filename
        uml_stm_export.SimpleSTM.parse(self, data)
                   
    def end_render(self) :
        f = open(self.filename, "a+")
        file_content = f.read()
        print(file_content)

        fsm_vars = "static FSMState state;\n"
        triggers = "typedef enum\n{\n"
        transitions = "static FSMTransition fsm_transitions[NB_TRANSITIONS] = {0};\n"
        transitions_init = "    /** Initialize transitions - cannot be done statically (non const states) */\n"
        init_func_decl = "static void init_fsm(void);\n\n"
        init_func_def = "void init_fsm(void)\n{{\n{}\n\n{}}}\n\n"
        state_init = ""
        guard_decls = self.FSM_GUARDS_DEFS
        guard_defs = self.FSM_GUARDS_DEFS
        action_decls = self.FSM_ACTIONS_DEFS
        action_defs = self.FSM_ACTIONS_DEFS
        consts = "#define NB_TRANSITIONS ({}U)\n\n"

        trans_id = 0
        for i, transition in enumerate(self.transitions) :
            if transition.source == "INITIAL_STATE" :
                init_body = "    /** Go to initial state */\n"
                if len(transition.guard.strip()) >  0 or len(transition.trigger.strip()) > 0 :
                    raise Exception("Initial transition cannot be triggered by an event, cannot have a guard")
                
                # initial transition can have an action
                if len(transition.action.strip()) > 0 :
                    init_body = "    {};\n".format(transition.action)
                if len(self.states[transition.target].iaction.strip()) > 0 :
                    init_body = "{}    {};\n".format(init_body, self.states[transition.target].iaction)
                # set initial state
                state_init = "{}    state = {}_STATE;\n".format(init_body, self.states[transition.target].name)

            splitted_trig = ""
            if len(transition.trigger) > 0 :
                splitted_trig = transition.trigger.split(",")
                splitted_trig = [trig.strip() for trig in splitted_trig]
                for trig in splitted_trig :
                    if " {}".format(trig) not in triggers :
                        if i != 0 :
                            triggers = "{},\n".format(triggers)
                        triggers = "{}    {}".format(triggers, trig.strip())

            trans_ref = "NULL"
            if len(transition.guard) > 0 :
                guard_decls = "{}static bool guard_{}(void);\n".format(guard_decls, i)
                guard_defs = "{}inline bool guard_{}(void)\n{{\n    return {};\n}}\n\n".format(guard_defs, 
                    i,
                    transition.guard)
                trans_ref = "&guard_{}".format(i)

            action_trans_ref = "NULL"
            state_action_decls, state_action_defs, action_trans_ref = self._generate_state_actions(i, transition.action, "action_trans")
            action_decls = "{}{}".format(action_decls, state_action_decls)
            action_defs = "{}{}".format(action_defs, state_action_defs)

            for trig in splitted_trig :
                transitions_init = "{}    fsm_transitions[{}].curr_state = {}_STATE;\n".format(
                    transitions_init,
                    trans_id,
                    transition.source)
                transitions_init = "{}    fsm_transitions[{}].next_state = {}_STATE;\n".format(
                    transitions_init,
                    trans_id,
                    transition.target)
                transitions_init = "{}    fsm_transitions[{}].trigger = {};\n".format(
                    transitions_init,
                    trans_id,
                    trig)
                transitions_init = "{}    fsm_transitions[{}].guard = {};\n".format(
                    transitions_init,
                    trans_id,
                    trans_ref)
                transitions_init = "{}    fsm_transitions[{}].trans_action = {};\n\n".format(
                    transitions_init,
                    trans_id,
                    action_trans_ref)
                trans_id += 1

        consts = consts.format(trans_id)
        init_func_def = init_func_def.format(transitions_init, state_init)
        triggers = "{}\n}}Trigger;\n".format(triggers)

        state_enum = "typedef enum\n{\n"
        states_var = ""
        for i, key in enumerate(self.states.keys()) :
            if len(key) == 0 :
                continue
            if i != 0 :
                state_enum = "{},\n".format(state_enum)
            state_enum = "{}    {}".format(state_enum, key)
            action_enter_ref = "NULL"
            action_exit_ref = "NULL"
            action_in_ref = "NULL"

            state_action_decls, state_action_defs, action_enter_ref = self._generate_state_actions("{}_state".format(key.lower()), self.states[key].iaction, "action_enter")
            action_decls = "{}{}".format(action_decls, state_action_decls)
            action_defs = "{}{}".format(action_defs, state_action_defs)

            state_action_decls, state_action_defs, action_exit_ref = self._generate_state_actions("{}_state".format(key.lower()), self.states[key].oaction, "action_exit")
            action_decls = "{}{}".format(action_decls, state_action_decls)
            action_defs = "{}{}".format(action_defs, state_action_defs)

            state_action_decls, state_action_defs, action_in_ref = self._generate_state_actions("{}_state".format(key.lower()), self.states[key].doaction, "action_in")
            action_decls = "{}{}".format(action_decls, state_action_decls)
            action_defs = "{}{}".format(action_defs, state_action_defs)

            states_var = "{}static const FSMState {}_STATE = \n{{\n    {},\n    {},\n    {},\n    {},\n}};\n\n".format(
                states_var, 
                key, 
                key, 
                action_enter_ref,
                action_exit_ref,
                action_in_ref)

        state_enum = "{}\n}}State;\n".format(state_enum)

        user_includes = CFSMExporter._get_user_code(file_content, "Includes")
        user_consts = CFSMExporter._get_user_code(file_content, "Consts")
        user_types = CFSMExporter._get_user_code(file_content, "Types")
        user_static_vars_decls = CFSMExporter._get_user_code(file_content, "User Static Variables Declarations")
        user_local_fcts_decls = CFSMExporter._get_user_code(file_content, "User Local Functions Declarations")
        user_global_fcts_defs = CFSMExporter._get_user_code(file_content, "User Global Functions Definitions")
        user_static_fcts_defs = CFSMExporter._get_user_code(file_content, "User Static Functions Definitions")

        f.truncate(0)
        f.write(self.CODE_PREAMBLE)
        f.write(user_includes)
        f.write(self.CONST_DEFS)
        f.write(consts)
        f.write(user_consts)        
        f.write(self.TYPE_DEFS)
        f.write(state_enum)
        f.write("\n{}\n".format(triggers))
        f.write(user_types)
        f.write(self.STATIC_FUNCS_DECLS)
        f.write(init_func_decl);
        f.write("{}\n".format(action_decls))
        f.write("{}\n".format(guard_decls))
        f.write(user_local_fcts_decls)
        f.write(self.STATIC_VARS)
        f.write(fsm_vars);
        f.write(states_var)
        f.write("{}\n".format(transitions))
        f.write(user_static_vars_decls)
        f.write(self.GLOBAL_FUNCS_DEFS)
        f.write("{}\n".format(user_global_fcts_defs))
        f.write(self.STATIC_FUNCS_DEFS)
        f.write(init_func_def);
        f.write(action_defs)
        f.write(guard_defs)
        f.write(user_static_fcts_defs)

        f.close()
        self.states = {}
        self.transitions = []

    # generate enter, exit, in actions for a given state action
    # returns a tuple of (function_declarations, functions_definitions, state_reference_action)
    @staticmethod
    def _generate_state_actions(state_name, state_action, action_name) :
        # reference on action function set in state variable
        ref_action = "NULL"
        action_decls = ""
        action_defs = ""
        if len(state_action) > 0 :
            splitted_actions = state_action.split(";")
            splitted_actions = [action.strip() for action in splitted_actions]
            # several function calls, group it in a "action_enter_the_state() method 
            action_decls = "static void {}_{}(void);\n".format(action_name, state_name)
            action_defs = "inline void {}_{}(void)\n{{\n".format(action_name, state_name)
            for action in splitted_actions :
                if len(action) > 0 :
                    action_defs = "{}    {};\n".format(action_defs, action.strip())
            action_defs = "{}}}\n\n".format(action_defs)
            ref_action = "&{}_{}".format(action_name, state_name)
        return (action_decls, action_defs, ref_action)

    @staticmethod
    def _get_user_code(content, section_name) :
        start_tag = "/** {} {} */\n".format(CFSMExporter.USER_CODE_BEGIN, section_name)
        end_tag = "/** {} {} */\n".format(CFSMExporter.USER_CODE_END, section_name)
        try :
            i = content.index(start_tag)
            j = content.index(end_tag)
            return content[i:j + len(end_tag)]
        except ValueError as e :
            return "{}{}".format(
                start_tag,
                end_tag)


# dia-python keeps a reference to the renderer class and uses it on demand
dia.register_export("State Machine C", "c", CFSMExporter())
