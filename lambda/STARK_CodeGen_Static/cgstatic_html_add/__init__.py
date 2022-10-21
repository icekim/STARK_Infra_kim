#STARK Code Generator component.
#Produces the customized static content for a STARK system

#Python Standard Library
import base64
import textwrap
import os
import importlib

#Private modules
prepend_dir = ""
if 'libstark' in os.listdir():
    prepend_dir = "libstark.STARK_CodeGen_Static."

cg_coltype  = importlib.import_module(f"{prepend_dir}cgstatic_controls_coltype")
cg_header   = importlib.import_module(f"{prepend_dir}cgstatic_html_generic_header")
cg_footer   = importlib.import_module(f"{prepend_dir}cgstatic_html_generic_footer")
cg_bodyhead = importlib.import_module(f"{prepend_dir}cgstatic_html_generic_bodyhead")
cg_loadmod  = importlib.import_module(f"{prepend_dir}cgstatic_html_generic_loadingmodal")

import convert_friendly_to_system as converter

def create(data):

    #project = data["Project Name"]
    entity      = data["Entity"]
    cols        = data["Columns"]
    pk          = data["PK"]
    rel_model   = data["Rel Model"]

    #Convert human-friendly names to variable-friendly names
    entity_varname = converter.convert_to_system_name(entity)
    pk_varname     = converter.convert_to_system_name(pk)

    source_code  = cg_header.create(data, "New")
    source_code += cg_bodyhead.create(data, "New")

    source_code += f"""\
        <!--<div class="container-unauthorized" v-if="!stark_permissions['{entity}|Add']">UNAUTHORIZED!</div>
        <div class="main-continer" v-if="stark_permissions['{entity}|Add']">-->
            <div class="container hidden" :style="{{visibility: visibility}}">
                <div class="row">
                    <div class="col">
                        <div class="my-auto">
                            <form class="border p-3">
                            <input type="hidden" id="orig_{pk_varname}" v-model="{entity_varname}.{pk_varname}">
                            <div class="form-group">
                                <label for="{pk_varname}">{pk}</label>
                                <b-form-input type="text" class="form-control" id="{pk_varname}" placeholder="" v-model="{entity_varname}.{pk_varname}" :state="metadata.{pk_varname}.state"></b-form-input>
                                <b-form-invalid-feedback>{{{{metadata.{pk_varname}.feedback}}}}</b-form-invalid-feedback>
                            </div>"""

    for col, col_type in cols.items():
        col_varname = converter.convert_to_system_name(col)
        html_control_code = cg_coltype.create({
            "col": col,
            "col_type": col_type,
            "col_varname": col_varname,
            "entity" : entity,
            "entity_varname": entity_varname
        })

        source_code += f"""
                            <b-form-group class="form-group" label="{col}" label-for="{col_varname}" :state="metadata.{col_varname}.state" :invalid-feedback="metadata.{col_varname}.feedback">
                                {html_control_code}
                            </b-form-group>"""

        if isinstance(col_type, dict) and col_type["type"] == "relationship":
            has_many_ux = col_type.get('has_many_ux', None)
            has_many = col_type.get('has_many')
            if has_many_ux: 
                rel_pk = rel_model[has_many].get('pk')
                rel_pk_varname = converter.convert_to_system_name(rel_pk)
                child_entity_varname = converter.convert_to_system_name(has_many)
                source_code += f"""
                            <template>
                                <!-- <a v-b-toggle class="text-decoration-none" :href="'#group-collapse-'+index" @click.prevent> -->
                                <a v-b-toggle class="text-decoration-none" @click.prevent>
                                    <span class="when-open"><img src="images/chevron-up.svg" class="filter-fill-svg-link" height="20rem"></span><span class="when-closed"><img src="images/chevron-down.svg" class="filter-fill-svg-link" height="20rem"></span>
                                    <span class="align-bottom">Document</span>
                                </a>
                                <!-- <b-collapse :id="'group-collapse-'+index" visible class="mt-0 mb-2 pl-2"> -->
                                <b-collapse visible class="mt-0 mb-2 pl-2">
                                    <div class="row">
                                        <div class="col-12">
                                            <div class="card">
                                                <div class="card-body">
                                                    <form class="repeater" enctype="multipart/form-data">
                                                        <div class="row" v-for="(field, index) in {child_entity_varname}">
                                                            <div class="form-group">
                                                                <b-form-group class="form-group" label="#">
                                                                    {{{{ index + 1 }}}}
                                                                </b-form-group>
                                                            </div>"""

                source_code += f"""
                                                            <div class="form-group">
                                                                <label for="{rel_pk_varname}">{rel_pk}</label>
                                                                <b-form-input type="text" class="form-control" id="{rel_pk_varname}" placeholder="" v-model="field.{rel_pk_varname}" :state="metadata.{rel_pk_varname}.state"></b-form-input>
                                                                <b-form-invalid-feedback>{{{{metadata.{rel_pk_varname}.feedback}}}}</b-form-invalid-feedback>
                                                            </div>"""

                
                for rel_col, rel_data in rel_model.items():
                    child_entity_varname = converter.convert_to_system_name(rel_col)
                    for rel_col_key, rel_col_type in rel_data.get('data').items():
                        rel_col_varname = converter.convert_to_system_name(rel_col_key)
                        rel_html_control_code = cg_coltype.create({
                            "col": rel_col_key,
                            "col_type": rel_col_type,
                            "col_varname": rel_col_varname,
                            "entity" : rel_col,
                            "entity_varname": child_entity_varname
                        })

                    source_code += f"""
                                                        <div class="form-group col-lg-2">
                                                            {rel_html_control_code}
                                                        </div>"""

                source_code += f"""
                                                            <div class="form-group col-lg-2 ">
                                                                <b-form-group class="form-group" label="Remove">
                                                                    <input type="button" class="btn bg-danger" alt="Delete" width="40" height="40" @click="root.RemoveField(index, '{child_entity_varname}')" value="X">
                                                                </b-form-group>
                                                            </div> 
                                                        </div>
                                                        <div>
                                                            <input type="button" class="btn btn-success mt-3 mt-lg-0" @click="root.AddField('{child_entity_varname}')" value="Add"/>
                                                        </div>
                                                    </form>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </b-collapse>
                                <hr><br>
                            </template>
                                                            

                """
    source_code += f"""
                            <button type="button" class="btn btn-secondary" onClick="window.location.href='{entity_varname}.html'">Back</button>
                            <button type="button" class="btn btn-primary float-right" onClick="root.add()">Add</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
"""

    source_code += cg_loadmod.create()
    source_code += cg_footer.create()

    return textwrap.dedent(source_code)