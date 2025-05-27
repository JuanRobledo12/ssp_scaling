import pandas as pd

class PreprocessingUtils:


    
    @staticmethod
    def subsector_dict_to_df(mapping: dict) -> pd.DataFrame:
        """
        Convert a subsector‐to‐code mapping dict into a DataFrame
        with columns ['subsector', 'code'].
        """
        # Turn dict items into a list of (subsector, code) tuples,
        # then build a DataFrame with appropriate column names.
        df = pd.DataFrame(list(mapping.items()), columns=['la_subsector', 'ssp_subsector'])
        return df
    
    @staticmethod
    def distribute_fc_gases(df: pd.DataFrame,
                            ssp_fc_gases: list[str],
                            keep_single: tuple[str] = ('ch4', 'n2o', 'co2')
                        ) -> pd.DataFrame:
        """
        For rows whose `gas` is NOT in keep_single, replace each such row with one
        row per gas in ssp_fc_gases, assigning each new row:
        value = original_value / len(ssp_fc_gases)
        Single-gas rows (ch4, n2o, co2) are preserved verbatim.

        Parameters
        ----------
        df : pd.DataFrame
            Must have columns ['subsector', 'gas', YEAR1, YEAR2, ...]
        ssp_fc_gases : list[str]
            The list of F-gas codes to expand into.
        keep_single : tuple[str]
            Gas names to leave alone.

        Returns
        -------
        pd.DataFrame
        """
        # Identify year columns
        year_cols = [c for c in df.columns if c not in ('subsector', 'gas')]

        # Keep single-gas rows
        df_single = df[df['gas'].isin(keep_single)].copy()

        # Rows to expand
        df_multi = df[~df['gas'].isin(keep_single)].copy()

        n = len(ssp_fc_gases)
        if n == 0:
            raise ValueError("ssp_fc_gases list must be non-empty")

        expanded_rows = []
        for _, row in df_multi.iterrows():
            # Distribute equally across all ssp_fc_gases
            for g in ssp_fc_gases:
                new = {'subsector': row['subsector'], 'gas': g}
                for yr in year_cols:
                    new[yr] = row[yr] / n
                expanded_rows.append(new)

        df_expanded = pd.DataFrame(expanded_rows,
                                columns=['subsector', 'gas'] + year_cols)

        # Combine and return
        return pd.concat([df_single, df_expanded], ignore_index=True)
