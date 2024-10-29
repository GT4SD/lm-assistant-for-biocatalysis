"""Enhanced MD Simulations tools and utilities."""

__copyright__ = """
MIT License

Copyright (c) 2024 GT4SD team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..configuration import BIOCATALYSIS_AGENT_CONFIGURATION
from .core import BiocatalysisAssistantBaseTool

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class SimulationConfiguration(BaseSettings):
    """Configuration values for the MDSimulation tool."""

    tool_dir: Path = Field(
        default_factory=lambda: BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path(
            "molecular_dynamics"
        ),
        description="Root directory for simulations.",
    )
    simulations_dir: Path = Field(
        default_factory=lambda: Path(
            BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("molecular_dynamics")
        )
        / "simulations",
        description="Simulations directory.",
    )
    minimization_dir: Path = Field(
        default_factory=lambda: Path(
            BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("molecular_dynamics")
        )
        / "simulations/minimization",
        description="Minimization directory.",
    )
    nvt_dir: Path = Field(
        default_factory=lambda: Path(
            BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("molecular_dynamics")
        )
        / "simulations/nvt",
        description="NVT directory.",
    )
    npt_dir: Path = Field(
        default_factory=lambda: Path(
            BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("molecular_dynamics")
        )
        / "simulations/npt",
        description="NPT directory.",
    )
    mdp_dir: Path = Field(
        default_factory=lambda: Path(
            BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("molecular_dynamics")
        )
        / "mdp_files",
        description="MDP files directory.",
    )
    run_dir: Path = Field(
        default_factory=lambda: Path(
            BIOCATALYSIS_AGENT_CONFIGURATION.get_tools_cache_path("molecular_dynamics")
        )
        / "run_files",
        description="Shell script files directory.",
    )

    model_config = SettingsConfigDict(env_prefix="MOLECULAR_DYNAMICS_")

    def get_mdp_path(self, stage: str) -> Path:
        """
        Get the path to the .mdp file for a given stage.

        Args:
            stage: The simulation stage.

        Returns:
            Path to the .mdp file.
        """
        return self.mdp_dir / f"{stage}.mdp"

    def get_sh_path(self, stage: str) -> Path:
        """
        Get the path to the .sh file for a given stage.

        Args:
            stage: The simulation stage.

        Returns:
            Path to the .sh file.
        """
        return self.run_dir / f"run_{stage}.sh"


SIMULATION_SETTINGS = SimulationConfiguration()

SIMULATION_DESCRIPTION = """
The MDSimulation Tool is designed to facilitate Molecular Dynamics (MD) simulations on protein structures.
The tool leverages the power of GROMACS, a highly versatile molecular dynamics package, to simulate biochemical molecules such as proteins, lipids, and nucleic acids.

Key Features:

1. Modular Design: The tool separates different simulation stages into modular classes—Minimization, NVT Equilibration, and NPT Equilibration—allowing for flexible configuration of the simulation process.
2. Configurable Parameters: Users can easily modify key simulation parameters directly within the tool without needing external configuration files. Default values are provided for critical parameters.
3. Dynamic Workflow: The tool can automatically run complete MD simulation pipelines (Minimization → NVT → NPT) or individual stages as needed. The stages are designed to run in a sequential manner—Minimization must run before NVT, and NVT must run before NPT.
4. Automated File Management: The tool dynamically handles simulation input and output files, including updates to MDP and shell script files.

How to Use:

To run the MDSimulation Tool, the user prepares a PDB file (protein structure) and specifies the desired simulation stages and their parameters. The tool can run one or more stages, and users can override the default parameter values by passing them via keyword arguments.

Example Usage:
# Running MD simulation starting with minimization, followed by NVT and NPT equilibration
(
    protein_strcuture.pdb,
    stages=['minimization', 'nvt', 'npt'],  # Running the three stages sequentially, Default is ['minimization]
    minimization={'nsteps': 100},            # Modifying the 'nsteps' parameter for minimization stage. Default is {}.
    nvt={'nsteps': 5000},            # Modifying the 'nsteps' parameter for nvt stage. Default is {}.
    npt={'nsteps': 5000},            # Modifying the 'nsteps' parameter for npt stage. Default is {}.
)

In the example:
- Stages: The user is running the three stages (minimization, nvt, npt) sequentially.
- minimization: The nsteps parameter is explicitly set to 100, meaning the minimization will run for 100 steps. Default parameters are used for NVT and NPT unless otherwise specified.

Default Values and Parameter Descriptions:

For each stage, there are key parameters that can be modified. If no parameters are provided for a particular stage, the tool will use the default values. The default sequence is to run Minimization → NVT → NPT, and each stage depends on the completion of the previous one.

Default Stage Sequence:
- Minimization → NVT Equilibration → NPT Equilibration

Default Parameters for Each Stage:

1. Minimization:
   - nsteps (default: 50000): The number of steps for the minimization phase. A larger value increases simulation time.
   - dt (default: 0.001): The time step in picoseconds for each simulation step. Smaller values improve accuracy but increase computational cost.

2. NVT Equilibration:
   - nsteps (default: 1000): Defines the number of steps for the NVT equilibration phase.
   - dt (default: 0.002): The time step for the simulation in picoseconds (2 femtoseconds).
   - ref_t (default: 300): The reference temperature in Kelvin. This keeps the system at a target temperature during NVT equilibration.

3. NPT Equilibration:
   - nsteps (default: 1000): The number of steps for the NPT equilibration phase.
   - dt (default: 0.002): The time step in picoseconds.
   - ref_t (default: 300): The reference temperature in Kelvin to keep the system at the target temperature.
   - Pcoupl (default: Parrinello-Rahman): The pressure coupling method, which ensures that pressure is controlled during the NPT phase.

Running the Tool:

1. Prepare the Protein Structure (PDB File):
   - The user must provide the path to the PDB file that contains the protein structure.
   
2. Specify the Stages:
   - The default is to run Minimization, followed by NVT Equilibration, and finally NPT Equilibration. These can be modified by providing a different sequence in the stages argument.

3. Modify Simulation Parameters:
   - Users can override the default parameters for each stage (e.g., nsteps, dt, ref_t, etc.) by passing them as keyword arguments. For example, you can pass minimization={'nsteps': 100} to modify the number of steps for the minimization phase.

Summary:

The MDSimulation Tool is a powerful, flexible solution for running Molecular Dynamics simulations on protein structures. It offers dynamic configuration of key parameters, supports a modular workflow with multiple simulation stages, and simplifies the simulation process by handling all file management automatically. The default workflow runs through Minimization, NVT Equilibration, and NPT Equilibration, but users can easily modify this to suit their research needs.
"""


class MDPFileUpdater:
    """Class for updating MDP files."""

    def update_file(self, file_path: Path, updates: Dict[str, Any]) -> Path:
        """
        Update the MDP file with the provided updates.

        Args:
            file_path: Path to the MDP file.
            updates: Dictionary of updates to apply.

        Returns:
            Path to the updated MDP file.
        """
        with Path.open(file_path, "r") as file:
            content = file.readlines()

        updated_content = []
        for line in content:
            key = line.split("=")[0].strip()
            if key in updates:
                updated_content.append(f"{key} = {updates[key]}\n")
            else:
                updated_content.append(line)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mdp", mode="w")
        with Path.open(Path(temp_file.name), "w") as file:
            file.writelines(updated_content)

        logger.info(f"Temporary .mdp file created at: {temp_file.name}")
        return Path(temp_file.name)


class SimulationStage(ABC):
    """Abstract base class for simulation stages."""

    def __init__(
        self, config: Dict[str, Any], stage_name: str, mdp_updater: MDPFileUpdater
    ):
        """
        Initialize simulation stages.

        Args:
            config: Configuration dictionary.
            stage_name: Name of the simulation stage.
            mdp_updater: MDPFileUpdater instance.
        """
        self.config = config
        self.stage_name = stage_name
        self.mdp_updater = mdp_updater

    @abstractmethod
    def run(self, input_file: Path, **kwargs) -> Path:
        """
        Run the simulation stage.

        Args:
            input_file: Path to the input file.

        Returns:
            Path to the output file.
        """
        pass

    def update_mdp_file(self, updates: Dict[str, Any]) -> Path:
        """
        Update the .mdp file with parameters from the updates.

        Args:
            updates: Dictionary of updates to apply.

        Returns:
            Path to the updated MDP file.
        """
        mdp_path = SIMULATION_SETTINGS.get_mdp_path(self.stage_name)
        return self.mdp_updater.update_file(mdp_path, updates)


class GenericSimulationStage(SimulationStage):
    """Generic simulation stage that can be used for minimization, NVT, and NPT."""

    def run(self, input_file: Path, **kwargs) -> Path:
        """
        Run the simulation stage.

        Args:
            input_file: Path to the input file.

        Returns:
            Path to the output file.
        """
        logger.info(f"Running {self.stage_name} on {input_file}")

        if kwargs:
            mdp_file = self.update_mdp_file(kwargs)
        else:
            mdp_file = SIMULATION_SETTINGS.get_mdp_path(self.stage_name)

        output_dir = getattr(SIMULATION_SETTINGS, f"{self.stage_name}_dir")

        subprocess.run(
            [
                "bash",
                SIMULATION_SETTINGS.get_sh_path(self.stage_name),
                str(input_file),
                str(output_dir),
                str(mdp_file),
            ],
            check=True,
        )

        output_file = output_dir / f"{self.stage_name}.gro"
        return output_file


class MDSimulation(BiocatalysisAssistantBaseTool):
    """
    Tool for performing MD simulations on protein structures.
    """

    name: str = "MDSimulation"
    description: str = SIMULATION_DESCRIPTION

    @staticmethod
    def check_requirements() -> bool:
        """
        Check if the required directories and files for MD simulation exist.

        Returns:
            Boolean indicating if all requirements are met.
        """
        try:
            for dir_path in [
                SIMULATION_SETTINGS.tool_dir,
                SIMULATION_SETTINGS.mdp_dir,
                SIMULATION_SETTINGS.run_dir,
                SIMULATION_SETTINGS.simulations_dir,
                SIMULATION_SETTINGS.minimization_dir,
                SIMULATION_SETTINGS.nvt_dir,
                SIMULATION_SETTINGS.npt_dir,
            ]:
                dir_path.mkdir(parents=True, exist_ok=True)

            for config_name in ["minimization", "nvt", "npt"]:
                mdp_file = SIMULATION_SETTINGS.get_mdp_path(config_name)
                if not mdp_file.exists():
                    raise FileNotFoundError(f"MDP file {mdp_file} not found.")

                sh_file = SIMULATION_SETTINGS.get_sh_path(config_name)
                if not sh_file.exists():
                    raise FileNotFoundError(f"Shell script {sh_file} not found.")

            try:
                subprocess.run(["gmx", "--version"], check=True, capture_output=True)
                from pymol import cmd

                _ = cmd
                return True
            except Exception as e:
                logger.warning(f"Error instantiating MDSimulation: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Error in checking requirements: {e}")
            raise

    @staticmethod
    def preprocess_structure(input_file: Path) -> Path:
        """
        Remove water, ligands, and other non-protein molecules from the input structure.

        Args:
            input_file: Path to the input PDB file.

        Returns:
            Path to the preprocessed PDB file.
        """
        from pymol import cmd

        output_file = input_file.parent / f"{input_file.stem}_protein_only.pdb"

        cmd.load(str(input_file), "structure")
        cmd.remove("not polymer")
        cmd.save(str(output_file), "structure")
        cmd.delete("all")

        return output_file

    def _run(
        self,
        pdb_file: Path,
        stages: List[str] = ["minimization", "nvt", "npt"],
        **kwargs,
    ) -> str:
        """
        Run MD simulations.

        Args:
            pdb_file: Path to the input PDB file.
            stages: List of simulation stages to run.

        Returns:
            String describing the simulation outcome.
        """
        try:
            if not Path(pdb_file).exists():
                raise FileNotFoundError(f"Input file {pdb_file} not found.")

            preprocessed_file = self.preprocess_structure(pdb_file)
            input_file = preprocessed_file

            for stage_name in stages:
                stage = GenericSimulationStage(
                    kwargs.get(stage_name, {}), stage_name, MDPFileUpdater()
                )
                input_file = stage.run(input_file, **kwargs.get(stage_name, {}))

            return f"MD simulation completed successfully. Final output: {input_file}"

        except Exception as e:
            logger.error(f"Error in MDSimulation: {e}")
            raise ValueError(f"Failed to run MD simulation: {str(e)}")

    async def _arun(self, *args, **kwargs) -> str:
        """
        Async method for MD simulation.

        Raises:
            NotImplementedError: Async execution is not implemented.
        """
        raise NotImplementedError("Async execution not implemented for MDSimulation.")
