# import packages/modules
import logging
from typing import Optional, List
from pyThermoLinkDB import build_components_model_source, build_model_source
from pyThermoLinkDB.models import ComponentModelSource, ModelSource
from pythermodb_settings.models import Component
from pyThermoDB import ComponentThermoDB
from pyThermoDB import build_component_thermodb_from_reference

# NOTE: logger
logger = logging.getLogger(__name__)

# SECTION: BUILD MODEL SOURCE


def build_model_source_from_reference(
        components: List[Component],
        reference_content: str,
        ignore_state_props: Optional[List[str]] = None,
) -> Optional[ModelSource]:

    try:
        # NOTE: build components thermodb
        thermodb_components: List[ComponentThermoDB] = []

        # iterate over components and build thermodb component from reference
        for comp in components:
            thermodb_component = build_component_thermodb_from_reference(
                component_name=comp.name,
                component_formula=comp.formula,
                component_state=comp.state,
                reference_content=reference_content,
                ignore_state_props=ignore_state_props,
            )
            if thermodb_component is None:
                logger.warning(
                    f"Component {comp.name} could not be built from reference. Skipping.")
                return None

            # add to list
            thermodb_components.append(thermodb_component)

        # NOTE: build model source
        # ! with partially matched rules
        component_model_source: List[ComponentModelSource] = build_components_model_source(
            components_thermodb=thermodb_components,
            rules=None,
        )

        # model source
        model_source: ModelSource = build_model_source(
            source=component_model_source,
        )

        # build datasource & equationsource
        datasource = model_source.data_source
        equationsource = model_source.equation_source

        # NOTE: model source
        model_source: ModelSource = ModelSource(
            data_source=datasource,
            equation_source=equationsource
        )

        # return
        return model_source
    except Exception as e:
        logger.error(f"Error in build_model_source_from_reference: {e}")
        return None
