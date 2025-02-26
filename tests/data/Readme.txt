/******************************************************************************************************************/
 *                                                                                                                 *
 *  The CIS PUMF is a “person file”, meaning that there is a record for each person in responding households. If   *
 *  the unit of analysis is not the person (for example the household, economic family or census family), users    *
 *  should retain only one record per unit of analysis. An easy way to do this is to keep only the record of the   *
 *  major income earner of the unit of analysis: :                                                                 *
 *                                                                                                                 *
 *       - if the unit of analysis is the economic family, keep only records where EFMJIE=1;                       *
 *       - if the unit of analysis is the household, keep only records where HHMJIE=1;                             *
 *       - if the unit of analysis is the census family, keep only records where CFMJIE=1.                         *
 *                                                                                                                 *
/******************************************************************************************************************/ 
