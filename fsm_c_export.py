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
reload(uml_stm_export)
class CFSMExporter(uml_stm_export.SimpleSTM):
    now = datetime.now()

    USER_CODE_BEGIN = "USER CODE BEGIN"
    USER_CODE_END = "USER CODE END"
    FSM_OVERWRITTEN_CODE_BEGIN = "/** FSM OVERWRITTEN CODE BEGIN **/"
    FSM_OVERWRITTEN_CODE_END = "/** FSM OVERWRITTEN CODE END **/"
    FSM_OVERWRITING_USER_CODE_BEGIN = "/** FSM OVERWRITING USER CODE BEGIN **/"
    FSM_OVERWRITING_USER_CODE_END = "/** FSM OVERWRITING USER CODE END **/"

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
        "*****************************************************************************/\n"

    INCLUDE_DEFS = \
        "/***************************************************************************\n"    + \
        "* Include Files/\n"                                                                + \
        "***************************************************************************/\n"    +\
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
        self.consts = "#define NB_TRANSITIONS ({}U)\n"
        self.static_vars = "static FSMState state;\n"
        self.triggers_enum = "typedef enum\n{\n"
        self.transitions_def = "static FSMTransition fsm_transitions[NB_TRANSITIONS] = {0};\n"
        self.transitions_init = "    /** Initialize transitions - cannot be done statically (non const states) */\n"
        self.global_func_decl = "void {fsm_name_lower}_fsm_init(void);\n\nvoid {fsm_name_lower}_fsm_update_on_trigger({fsm_type_name}Trigger);\n\nvoid {fsm_name_lower}_fsm_update(void);\n\n"
        self.init_func_def = "void\n{}_fsm_init(void)\n{{\n{}{}}}\n\n"
        self.update_fsm_func_def = "void\n{fsm_name_lower}_fsm_update_on_trigger({fsm_type_name}Trigger trigger)\n{{\n    fsm_update_on_trigger(&state, fsm_transitions, NB_TRANSITIONS, trigger);\n}}\n\nvoid\n{fsm_name_lower}_fsm_update(void)\n{{\n    fsm_update(state);\n}}\n\n"
        self.state_init = ""
        self.guard_decls = self.FSM_GUARDS_DEFS
        self.guard_defs = self.FSM_GUARDS_DEFS
        self.action_decls = self.FSM_ACTIONS_DEFS
        self.action_defs = self.FSM_ACTIONS_DEFS
        self.state_enum = "typedef enum{\n"

    def begin_render (self, data, src_filename):
        self.src_filename = src_filename
        self.header_filename = "{}.h".format(os.path.splitext(self.src_filename)[0])
        self.header_file = open(self.header_filename, "a+")
        self.header_file_content = self.header_file.read()
        self.src_file = open(self.src_filename, "a+")
        self.src_file_content = self.src_file.read()

        r = re.search("(.+)_fsm.c", os.path.basename(self.src_filename))
        if r :
            self.fsm_name = r.groups()[0]
        else :
            print("bad src_filename given - cannot get fsm name")
            self.fsm_name = ""
        self.global_func_decl = self.global_func_decl.format(fsm_name_lower = self.fsm_name.lower(), fsm_type_name = CFSMExporter._convert_to_c_type_name(self.fsm_name))
        self.update_fsm_func_def = self.update_fsm_func_def.format(fsm_name_lower = self.fsm_name.lower(), fsm_type_name = CFSMExporter._convert_to_c_type_name(self.fsm_name))

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
            trans_action_decl, trans_action_def, trans_action_ref = self._generate_action("void", "action_trans_{}".format(i), "void", transition.action)

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
        self.triggers_enum = "{}\n}}{}Trigger;\n".format(self.triggers_enum, CFSMExporter._convert_to_c_type_name(self.fsm_name))

        for i, key in enumerate(self.states.keys()) :
            if len(key) == 0 :
                continue
            if i != 0 :
                self.state_enum = "{},\n".format(self.state_enum)
            self.state_enum = "{}    {}".format(self.state_enum, key)
            action_enter_ref = "NULL"
            action_exit_ref = "NULL"
            action_in_ref = "NULL"

            state_action_decl, state_action_def, action_enter_ref = self._generate_action("void", "action_enter_{}_state".format(key.lower()), "void", self.states[key].iaction)
            self.action_decls = "{}{}".format(self.action_decls, state_action_decl)
            self.action_defs = "{}{}".format(self.action_defs, state_action_def)

            state_action_decl, state_action_def, action_exit_ref = self._generate_action("void", "action_exit_{}_state".format(key.lower()), "void", self.states[key].oaction)
            self.action_decls = "{}{}".format(self.action_decls, state_action_decl)
            self.action_defs = "{}{}".format(self.action_defs, state_action_def)

            state_action_decl, state_action_def, action_in_ref = self._generate_action("void", "action_in_{}_state".format(key.lower()), "void", self.states[key].doaction)
            self.action_decls = "{}{}".format(self.action_decls, state_action_decl)
            self.action_defs = "{}{}".format(self.action_defs, state_action_def)

            self.static_vars = "{}static const FSMState {}_STATE = \n{{\n    {},\n    {},\n    {},\n    {},\n}};\n".format(
                self.static_vars,
                key, 
                key, 
                action_enter_ref,
                action_exit_ref,
                action_in_ref)

        self.state_enum = "{}\n}}{}State;\n".format(self.state_enum, CFSMExporter._convert_to_c_type_name(self.fsm_name))

        self._write_c_file()
        self._write_h_file()

        self.states = {}
        self.transitions = []


    def _write_c_file(self) :
        user_includes = self._get_user_code("Includes")
        user_consts = self._get_user_code("Consts")
        user_types = self._get_user_code("Types")
        user_static_vars = self._get_user_code("User Static Variables Declarations")
        user_local_fcts_decls = self._get_user_code("User Local Functions Declarations")
        user_global_fcts_defs = self._get_user_code("User Global Functions Definitions")
        user_static_fcts_defs = self._get_user_code("User Static Functions Definitions")

        self.src_file.truncate(0)
        self.src_file.write(self.CODE_PREAMBLE.format(
            fsm_filename = os.path.basename(self.src_filename)))
        self.src_file.write(self.INCLUDE_DEFS.format(
            headers = "#include \"fsm.h\"\n#include \"{}\"\n#include <stddef.h>\n".format(os.path.basename(self.header_filename))))
        self.src_file.write(user_includes)

        self.src_file.write(self.CONST_DEFS)
        self.src_file.write("{}\n".format(self.consts))
        self.src_file.write(user_consts)   

        self.src_file.write(self.TYPE_DEFS)
        self.src_file.write(self.state_enum)
        self.src_file.write("\n{}".format(user_types))

        self.src_file.write(self.STATIC_FUNCS_DECLS)
        self.src_file.write(self.action_decls)
        self.src_file.write("\n{}".format(self.guard_decls))
        self.src_file.write("\n{}".format(user_local_fcts_decls))

        self.src_file.write(self.STATIC_VARS)
        self.src_file.write(self.static_vars);
        self.src_file.write("\n{}".format(self.transitions_def))
        self.src_file.write("\n{}".format(user_static_vars))

        self.src_file.write(self.GLOBAL_FUNCS_DEFS)
        self.src_file.write(self.init_func_def)
        self.src_file.write("\n{}".format(self.update_fsm_func_def))
        self.src_file.write("\n{}".format(user_global_fcts_defs))

        self.src_file.write(self.STATIC_FUNCS_DEFS)
        self.src_file.write(self.action_defs)
        self.src_file.write("\n{}".format(self.guard_defs))
        self.src_file.write("\n{}".format(user_static_fcts_defs))

        self.src_file.close()

    def _write_h_file(self) :        
        user_includes = self._get_user_code("Includes")
        user_consts = self._get_user_code("Consts")
        user_types = self._get_user_code("Types")
        user_global_fcts_defs = self._get_user_code("User Global Functions Declarations")

        self.header_file.truncate(0)
        self.header_file.write(self.CODE_PREAMBLE.format(fsm_filename = os.path.basename(self.header_filename)))
        self.header_file.write(self.HEADER_DEF_BEGIN.format(fsm_name = self.fsm_name.upper()))
        self.header_file.write(self.INCLUDE_DEFS.format(headers = ""))      
        self.header_file.write("{}".format(user_includes))

        self.header_file.write(self.CONST_DEFS)
        self.header_file.write("\n{}".format(user_consts))     

        self.header_file.write(self.TYPE_DEFS)
        self.header_file.write(self.triggers_enum)
        self.header_file.write("\n{}".format(user_types))

        self.header_file.write(self.GLOBAL_FUNCS_DECLS)
        self.header_file.write(self.global_func_decl);
        self.header_file.write("\n{}".format(user_global_fcts_defs))

        self.header_file.write(self.HEADER_DEF_END.format(fsm_name = self.fsm_name.upper()))

        self.header_file.close()        

    # checks if user overwritten generated code
    # in this case, a comment with FSM model code is added
    def _generate_action_def(self, model_action_raw_def, action_ret, action_name, action_args) :
        action_def_proto = "{action_ret}\n{action_name}({action_args})".format(action_ret=action_ret, action_name=action_name, action_args=action_args)
        action_def = "{action_def_proto}\n{{\n{action_body}}}\n\n"
        model_action_body = ""

        if len(model_action_raw_def) > 0 :
            splitted_actions = model_action_raw_def.split(";")
            splitted_actions = [action.strip() for action in splitted_actions]
            for action in splitted_actions :
                if len(action) > 0 :
                    model_action_body = "{}    {};\n".format(model_action_body, action.strip())
        try :
            i = self.src_file_content.index("{}\n{{".format(action_def_proto))
        except ValueError as e :
            # function not defined before 
            return action_def.format(action_def_proto=action_def_proto, action_body=model_action_body)

        try :
            j = self.src_file_content[i:].index("\n}\n")
        except ValueError as e :    
            raise Exception("Cannot find end of {} definition".format(action_name))

        old_action_def = self.src_file_content[i:i+j+2]

        try :
            k = old_action_def.index("{{\n{}}}".format(model_action_body))
            # FSM model code not overwritten
            return action_def.format(action_def_proto=action_def_proto, action_body=model_action_body)

        except ValueError as e :
            # check if already overwriting FSM model code 
            if CFSMExporter.FSM_OVERWRITING_USER_CODE_BEGIN in old_action_def :
                overwriting_body = CFSMExporter._string_between(old_action_def, CFSMExporter.FSM_OVERWRITING_USER_CODE_BEGIN, "    {}".format(CFSMExporter.FSM_OVERWRITING_USER_CODE_END))
            else :
                overwriting_body = old_action_def[old_action_def.index("{")+1:-1]

            # function definition overwritten, add a comment indicating 
            # function model definition has been overwritten and add 
            # commented model code followed by user code
            old_action_def[old_action_def.index("{"):i+j+1]
            action_body = "    {}\n    /*\n{}    */\n    {}".format(
                CFSMExporter.FSM_OVERWRITTEN_CODE_BEGIN, 
                model_action_body, 
                CFSMExporter.FSM_OVERWRITTEN_CODE_END)

            action_body = "{}\n\n    {}{}    {}\n".format(
                action_body,
                CFSMExporter.FSM_OVERWRITING_USER_CODE_BEGIN,
                overwriting_body,
                CFSMExporter.FSM_OVERWRITING_USER_CODE_END)

            return action_def.format(action_def_proto=action_def_proto, action_body=action_body)

    # generate function declaration, definitions, reference
    # returns a tuple of (function_declarations, functions_definitions, state_reference_action)
    def _generate_action(self, func_ret, func_name, func_args, model_action_raw_def) :
        # reference on action function set in state variable
        ref_action = "NULL"
        action_decl = ""
        action_def = ""
        if len(model_action_raw_def) > 0 :
            action_decl = "static {} {}({});\n".format(func_ret, func_name, func_args)
            action_def = self._generate_action_def(model_action_raw_def, func_ret, func_name, func_args)
            ref_action = "&{}".format(func_name)
        return (action_decl, action_def, ref_action)

    def _get_user_code(self, section_name) :
        start_tag = "/** {} {} */\n".format(CFSMExporter.USER_CODE_BEGIN, section_name)
        end_tag = "/** {} {} */\n".format(CFSMExporter.USER_CODE_END, section_name)
        return "{}{}{}".format(
                start_tag,
                CFSMExporter._string_between(self.src_file_content, start_tag, end_tag),
                end_tag)

    @staticmethod
    def _string_between(str, start_str, end_str) :
        try :
            i = str.index(start_str)
            j = str.index(end_str)
            return str[i+len(start_str):j]
        except ValueError as e :
            return ""

    #convert given name from your_Type to YourType
    @staticmethod
    def _convert_to_c_type_name(name) :
        upper = False
        ret = ""
        for c in name.capitalize() :
            if c == "_" :
                upper = True
            elif upper :
                ret = ret + c.upper()
                upper = False
            else :
                ret = ret + c
        return ret

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

# dia-python keeps a reference to the renderer class and uses it on demand
dia.register_export("State Machine C", "c", CFSMExporter())
