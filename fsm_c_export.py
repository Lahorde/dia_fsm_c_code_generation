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
import os
import re
import sys
import uml_stm_export
import shutil
from datetime import datetime

class CFSMExporter(uml_stm_export.SimpleSTM):
    now = datetime.now()

    USER_CODE_BEGIN = "USER CODE BEGIN"
    USER_CODE_END = "USER CODE END"

    CODE_PREAMBLE = \
        "/******************************************************************************\n" + \
        "* @file    {fsm_filename}\n"                                                  + \
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
        "{headers}\n"                                                            


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

    GLOBAL_FUNCS_DECLS = \
        "/***************************************************************************\n" + \
        "* Global Functions Declarations                                              \n" + \
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

    HEADER_DEF_BEGIN = \
        "#ifndef {fsm_name}_FSM_H\n"      + \
        "#define {fsm_name}_FSM_H\n"      + \
        "\n"                              + \
        "#ifdef __cplusplus\n"            + \
        "extern \"C\"\n"                  + \
        "{{\n"                            + \
        "#endif\n"

    HEADER_DEF_END = \
        "#ifdef __cplusplus\n"      + \
        "}}\n"                      + \
        "#endif\n"                  + \
        "\n"                        + \
        "#endif /* {fsm_name}_FSM_H */"

    def __init__(self):
        uml_stm_export.SimpleSTM.__init__(self)
        self.src_filename = ""
        self.consts = "#define NB_TRANSITIONS ({}U)\n\n"
        self.static_vars = "static FSMState state;\n"
        self.triggers_enum = "typedef enum\n{\n"
        self.transitions_def = "static FSMTransition fsm_transitions[NB_TRANSITIONS] = {0};\n"
        self.transitions_init = "    /** Initialize transitions - cannot be done statically (non const states) */\n"
        self.global_func_decl = "void {fsm_name_lower}_fsm_init(void);\n\nvoid {fsm_name_lower}_fsm_update_on_trigger({fsm_name_capitalized}Trigger);\n\nvoid {fsm_name_lower}_fsm_update(void);\n\n"
        self.init_func_def = "void\n{}_fsm_init(void)\n{{\n{}{}}}\n\n"
        self.update_fsm_func_def = "void\n{fsm_name_lower}_fsm_update_on_trigger({fsm_name_capitalized}Trigger trigger)\n{{\n    fsm_update_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, trigger);\n}}\n\nvoid\n{fsm_name_lower}_fsm_update(void)\n{{\n    fsm_update(state);\n}}\n\n"
        self.state_init = ""
        self.guard_decls = self.FSM_GUARDS_DEFS
        self.guard_defs = self.FSM_GUARDS_DEFS
        self.action_decls = self.FSM_ACTIONS_DEFS
        self.action_defs = self.FSM_ACTIONS_DEFS
        self.state_enum = "typedef enum\n{\n"

    def begin_render (self, data, src_filename):
        self.src_filename = src_filename
        self.header_filename = "{}.h".format(os.path.splitext(self.src_filename)[0])
        r = re.search("(.+)_fsm.c", os.path.basename(self.src_filename))
        if r :
            self.fsm_name = r.groups()[0]
        else :
            print("bad src_filename given - cannot get fsm name")
            self.fsm_name = ""
        self.global_func_decl = self.global_func_decl.format(fsm_name_lower = self.fsm_name.lower(), fsm_name_capitalized = self.fsm_name.capitalize())
        self.update_fsm_func_def = self.update_fsm_func_def.format(fsm_name_lower = self.fsm_name.lower(), fsm_name_capitalized = self.fsm_name.capitalize())

        uml_stm_export.SimpleSTM.parse(self, data)
        script_path = os.path.dirname(os.path.realpath(__file__))
        
        # copy fsm lib to generated fsm folder
        fsm_dest_lib_path = "{}/fsm".format(os.path.dirname(self.src_filename))
        if os.path.isdir(fsm_dest_lib_path) :
            shutil.rmtree(fsm_dest_lib_path)
        shutil.copytree("{}/fsm_c_lib".format(script_path), fsm_dest_lib_path)
                   
    def end_render(self) :
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
                self.state_init = "{}    state = {}_STATE;\n".format(init_body, self.states[transition.target].name)

            splitted_trig = ""
            if len(transition.trigger) > 0 :
                splitted_trig = transition.trigger.split(",")
                splitted_trig = [trig.strip() for trig in splitted_trig]
                for trig in splitted_trig :
                    if " {}".format(trig) not in self.triggers_enum :
                        if i != 0 :
                            self.triggers_enum = "{},\n".format(self.triggers_enum)
                        self.triggers_enum = "{}    {}_TRIG".format(self.triggers_enum, trig.strip())

            trans_ref = "NULL"
            if len(transition.guard) > 0 :
                guard_body = "{{\n    return {};\n}}".format(transition.guard)
                func_name = CFSMExporter._guard_already_defined(guard_body, self.guard_defs)
                if func_name :
                    trans_ref = "&{}".format(func_name)
                else :
                    self.guard_decls = "{}static bool guard_{}(void);\n".format(self.guard_decls, i)
                    self.guard_defs = "{}bool\nguard_{}(void)\n{}\n\n".format(self.guard_defs, 
                    i,
                    guard_body)
                    trans_ref = "&guard_{}".format(i)

            action_trans_ref = "NULL"
            trans_action_decl, trans_action_def, trans_action_ref = self._generate_function("void", "action_trans_{}".format(i), "void", transition.action)

            func_name = CFSMExporter._trans_action_already_defined(trans_action_def, self.action_defs)
            if func_name :
                trans_action_ref = "&{}".format(func_name)
            else :
                self.action_decls = "{}{}".format(self.action_decls, trans_action_decl)
                self.action_defs = "{}{}".format(self.action_defs, trans_action_def)

            for trig in splitted_trig :
                self.transitions_init = "{}    fsm_transitions[{}].curr_state = {}_STATE;\n".format(
                    self.transitions_init,
                    trans_id,
                    transition.source)
                self.transitions_init = "{}    fsm_transitions[{}].next_state = {}_STATE;\n".format(
                    self.transitions_init,
                    trans_id,
                    transition.target)
                self.transitions_init = "{}    fsm_transitions[{}].trigger = {}_TRIG;\n".format(
                    self.transitions_init,
                    trans_id,
                    trig)
                self.transitions_init = "{}    fsm_transitions[{}].guard = {};\n".format(
                    self.transitions_init,
                    trans_id,
                    trans_ref)
                self.transitions_init = "{}    fsm_transitions[{}].trans_action = {};\n\n".format(
                    self.transitions_init,
                    trans_id,
                    trans_action_ref)
                trans_id += 1

        self.consts = self.consts.format(trans_id)
        self.init_func_def = self.init_func_def.format(self.fsm_name.lower(), self.transitions_init, self.state_init)
        self.triggers_enum = "{}\n}}{}Trigger;\n".format(self.triggers_enum, self.fsm_name.capitalize())

        for i, key in enumerate(self.states.keys()) :
            if len(key) == 0 :
                continue
            if i != 0 :
                self.state_enum = "{},\n".format(self.state_enum)
            self.state_enum = "{}    {}".format(self.state_enum, key)
            action_enter_ref = "NULL"
            action_exit_ref = "NULL"
            action_in_ref = "NULL"

            state_action_decl, state_action_def, action_enter_ref = self._generate_function("void", "action_enter_{}_state".format(key.lower()), "void", self.states[key].iaction)
            self.action_decls = "{}{}".format(self.action_decls, state_action_decl)
            self.action_defs = "{}{}".format(self.action_defs, state_action_def)

            state_action_decl, state_action_def, action_exit_ref = self._generate_function("void", "action_exit_{}_state".format(key.lower()), "void", self.states[key].oaction)
            self.action_decls = "{}{}".format(self.action_decls, state_action_decl)
            self.action_defs = "{}{}".format(self.action_defs, state_action_def)

            state_action_decl, state_action_def, action_in_ref = self._generate_function("void", "action_in_{}_state".format(key.lower()), "void", self.states[key].doaction)
            self.action_decls = "{}{}".format(self.action_decls, state_action_decl)
            self.action_defs = "{}{}".format(self.action_defs, state_action_def)

            self.static_vars = "{}static const FSMState {}_STATE = \n{{\n    {},\n    {},\n    {},\n    {},\n}};\n\n".format(
                self.static_vars,
                key, 
                key, 
                action_enter_ref,
                action_exit_ref,
                action_in_ref)

        self.state_enum = "{}\n}}{}State;\n".format(self.state_enum, self.fsm_name.capitalize())

        self._write_c_file()
        self._write_h_file()

        self.states = {}
        self.transitions = []


    def _write_c_file(self) :
        f = open(self.src_filename, "a+")

        file_content = f.read()
        user_includes = CFSMExporter._get_user_code(file_content, "Includes")
        user_consts = CFSMExporter._get_user_code(file_content, "Consts")
        user_types = CFSMExporter._get_user_code(file_content, "Types")
        user_static_vars = CFSMExporter._get_user_code(file_content, "User Static Variables Declarations")
        user_local_fcts_decls = CFSMExporter._get_user_code(file_content, "User Local Functions Declarations")
        user_global_fcts_defs = CFSMExporter._get_user_code(file_content, "User Global Functions Definitions")
        user_static_fcts_defs = CFSMExporter._get_user_code(file_content, "User Static Functions Definitions")

        f.truncate(0)
        f.write(self.CODE_PREAMBLE.format(
            fsm_filename = os.path.basename(self.src_filename), 
            headers = "#include \"fsm.h\"\n#include \"{}\"\n#include <stddef.h>\n".format(os.path.basename(self.header_filename))))
        f.write(user_includes)
        f.write(self.CONST_DEFS)
        f.write(self.consts)
        f.write(user_consts)        
        f.write(self.TYPE_DEFS)
        f.write(self.state_enum)
        f.write(user_types)
        f.write(self.STATIC_FUNCS_DECLS)
        f.write("{}\n".format(self.action_decls))
        f.write("{}\n".format(self.guard_decls))
        f.write(user_local_fcts_decls)
        f.write(self.STATIC_VARS)
        f.write(self.static_vars);
        f.write("{}\n".format(self.transitions_def))
        f.write(user_static_vars)
        f.write(self.GLOBAL_FUNCS_DEFS)
        f.write("{}\n".format(user_global_fcts_defs))
        f.write(self.init_func_def);
        f.write(self.update_fsm_func_def)
        f.write(self.STATIC_FUNCS_DEFS)
        f.write(self.action_defs)
        f.write(self.guard_defs)
        f.write(user_static_fcts_defs)

        f.close()

    def _write_h_file(self) :
        f = open(self.header_filename, "a+")
        
        file_content = f.read()
        user_includes = CFSMExporter._get_user_code(file_content, "Includes")
        user_consts = CFSMExporter._get_user_code(file_content, "Consts")
        user_types = CFSMExporter._get_user_code(file_content, "Types")
        user_static_vars = CFSMExporter._get_user_code(file_content, "User Static Variables Declarations")
        user_local_fcts_decls = CFSMExporter._get_user_code(file_content, "User Local Functions Declarations")
        user_global_fcts_defs = CFSMExporter._get_user_code(file_content, "User Global Functions Definitions")
        user_static_fcts_defs = CFSMExporter._get_user_code(file_content, "User Static Functions Definitions")

        f.truncate(0)
        f.write(self.CODE_PREAMBLE.format(fsm_filename = os.path.basename(self.header_filename), headers = ""))
        f.write(user_includes)
        f.write(self.HEADER_DEF_BEGIN.format(fsm_name = self.fsm_name.upper()))
        f.write(self.CONST_DEFS)
        f.write(user_consts)        
        f.write(self.TYPE_DEFS)
        f.write("{}\n".format(self.triggers_enum))
        f.write(user_types)
        f.write(self.GLOBAL_FUNCS_DECLS)
        f.write(self.global_func_decl);
        f.write(self.HEADER_DEF_END.format(fsm_name = self.fsm_name.upper()))

        f.close()        

    # generate function declaration, definitions, reference
    # returns a tuple of (function_declarations, functions_definitions, state_reference_action)
    @staticmethod
    def _generate_function(func_ret, func_name, func_args, body) :
        # reference on action function set in state variable
        ref_action = "NULL"
        action_decls = ""
        action_defs = ""
        if len(body) > 0 :
            splitted_actions = body.split(";")
            splitted_actions = [action.strip() for action in splitted_actions]
            # several function calls, group it in function body 
            action_decls = "static {} {}({});\n".format(func_ret, func_name, func_args)
            action_defs = "{}\n{}({})\n{{\n".format(func_ret, func_name, func_args)
            for action in splitted_actions :
                if len(action) > 0 :
                    action_defs = "{}    {};\n".format(action_defs, action.strip())
            action_defs = "{}}}\n\n".format(action_defs)
            ref_action = "&{}".format(func_name)
        return (action_decls, action_defs, ref_action)


    @staticmethod
    def _guard_already_defined(func_body, func_defs) :
        if func_body in func_defs :
            return re.findall("bool\n(guard_[0-9])\(void\)\n", func_defs[:func_defs.index(func_body)], re.DOTALL)[-1]
        return None

    @staticmethod
    def _trans_action_already_defined(func_def, func_defs) :
        return CFSMExporter._function_already_defined(func_def, func_defs, "void", "action_trans_[0-9]+", "void")

    # checks if a function with same definition but having a different name
    # has already been defined in given function definitions
    # returns 
    @staticmethod
    def _function_already_defined(func_def, func_defs, func_ret, func_name, func_params) :
        # extract func body
        ret = re.search("{}\n{}\({}\)\n({{\n.*\n}})".format(func_ret, func_name, func_params), func_def, re.DOTALL)
        if ret :
            func_body = ret.groups()[0]
            if func_body in func_defs :
                return re.findall("{}\n({})\({}\)\n".format(func_ret, func_name, func_params), func_defs[:func_defs.index(func_body)], re.DOTALL)[-1]
        return None


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
