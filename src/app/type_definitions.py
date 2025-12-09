from pydantic import BaseModel, Field, ConfigDict

class NetworkTrafficData(BaseModel):
    """
    Model input representing the 69 features required by the Scaler/Model.
    Field names match the scaler feature names exactly.
    """
    model_config = ConfigDict(populate_by_name=True)

    Protocol: int
    Flow_Duration: float = Field(..., alias='Flow Duration')
    Tot_Fwd_Pkts: float = Field(..., alias='Tot Fwd Pkts')
    Tot_Bwd_Pkts: float = Field(..., alias='Tot Bwd Pkts')
    TotLen_Fwd_Pkts: float = Field(..., alias='TotLen Fwd Pkts')
    TotLen_Bwd_Pkts: float = Field(..., alias='TotLen Bwd Pkts')
    Fwd_Pkt_Len_Max: float = Field(..., alias='Fwd Pkt Len Max')
    Fwd_Pkt_Len_Min: float = Field(..., alias='Fwd Pkt Len Min')
    Fwd_Pkt_Len_Mean: float = Field(..., alias='Fwd Pkt Len Mean')
    Fwd_Pkt_Len_Std: float = Field(..., alias='Fwd Pkt Len Std')
    Bwd_Pkt_Len_Max: float = Field(..., alias='Bwd Pkt Len Max')
    Bwd_Pkt_Len_Min: float = Field(..., alias='Bwd Pkt Len Min')
    Bwd_Pkt_Len_Mean: float = Field(..., alias='Bwd Pkt Len Mean')
    Bwd_Pkt_Len_Std: float = Field(..., alias='Bwd Pkt Len Std')
    Flow_Byts_s: float = Field(..., alias='Flow Byts/s')
    Flow_Pkts_s: float = Field(..., alias='Flow Pkts/s')
    Flow_IAT_Mean: float = Field(..., alias='Flow IAT Mean')
    Flow_IAT_Std: float = Field(..., alias='Flow IAT Std')
    Flow_IAT_Max: float = Field(..., alias='Flow IAT Max')
    Flow_IAT_Min: float = Field(..., alias='Flow IAT Min')
    Fwd_IAT_Tot: float = Field(..., alias='Fwd IAT Tot')
    Fwd_IAT_Mean: float = Field(..., alias='Fwd IAT Mean')
    Fwd_IAT_Std: float = Field(..., alias='Fwd IAT Std')
    Fwd_IAT_Max: float = Field(..., alias='Fwd IAT Max')
    Fwd_IAT_Min: float = Field(..., alias='Fwd IAT Min')
    Bwd_IAT_Tot: float = Field(..., alias='Bwd IAT Tot')
    Bwd_IAT_Mean: float = Field(..., alias='Bwd IAT Mean')
    Bwd_IAT_Std: float = Field(..., alias='Bwd IAT Std')
    Bwd_IAT_Max: float = Field(..., alias='Bwd IAT Max')
    Bwd_IAT_Min: float = Field(..., alias='Bwd IAT Min')
    Fwd_PSH_Flags: float = Field(..., alias='Fwd PSH Flags')
    Fwd_URG_Flags: float = Field(..., alias='Fwd URG Flags')
    Fwd_Header_Len: float = Field(..., alias='Fwd Header Len')
    Bwd_Header_Len: float = Field(..., alias='Bwd Header Len')
    Fwd_Pkts_s: float = Field(..., alias='Fwd Pkts/s')
    Bwd_Pkts_s: float = Field(..., alias='Bwd Pkts/s')
    Pkt_Len_Min: float = Field(..., alias='Pkt Len Min')
    Pkt_Len_Max: float = Field(..., alias='Pkt Len Max')
    Pkt_Len_Mean: float = Field(..., alias='Pkt Len Mean')
    Pkt_Len_Std: float = Field(..., alias='Pkt Len Std')
    Pkt_Len_Var: float = Field(..., alias='Pkt Len Var')
    FIN_Flag_Cnt: float = Field(..., alias='FIN Flag Cnt')
    SYN_Flag_Cnt: float = Field(..., alias='SYN Flag Cnt')
    RST_Flag_Cnt: float = Field(..., alias='RST Flag Cnt')
    PSH_Flag_Cnt: float = Field(..., alias='PSH Flag Cnt')
    ACK_Flag_Cnt: float = Field(..., alias='ACK Flag Cnt')
    URG_Flag_Cnt: float = Field(..., alias='URG Flag Cnt')
    CWE_Flag_Count: float = Field(..., alias='CWE Flag Count')
    ECE_Flag_Cnt: float = Field(..., alias='ECE Flag Cnt')
    Down_Up_Ratio: float = Field(..., alias='Down/Up Ratio')
    Pkt_Size_Avg: float = Field(..., alias='Pkt Size Avg')
    Fwd_Seg_Size_Avg: float = Field(..., alias='Fwd Seg Size Avg')
    Bwd_Seg_Size_Avg: float = Field(..., alias='Bwd Seg Size Avg')
    Subflow_Fwd_Pkts: float = Field(..., alias='Subflow Fwd Pkts')
    Subflow_Fwd_Byts: float = Field(..., alias='Subflow Fwd Byts')
    Subflow_Bwd_Pkts: float = Field(..., alias='Subflow Bwd Pkts')
    Subflow_Bwd_Byts: float = Field(..., alias='Subflow Bwd Byts')
    Init_Fwd_Win_Byts: float = Field(..., alias='Init Fwd Win Byts')
    Init_Bwd_Win_Byts: float = Field(..., alias='Init Bwd Win Byts')
    Fwd_Act_Data_Pkts: float = Field(..., alias='Fwd Act Data Pkts')
    Fwd_Seg_Size_Min: float = Field(..., alias='Fwd Seg Size Min')
    Active_Mean: float = Field(..., alias='Active Mean')
    Active_Std: float = Field(..., alias='Active Std')
    Active_Max: float = Field(..., alias='Active Max')
    Active_Min: float = Field(..., alias='Active Min')
    Idle_Mean: float = Field(..., alias='Idle Mean')
    Idle_Std: float = Field(..., alias='Idle Std')
    Idle_Max: float = Field(..., alias='Idle Max')
    Idle_Min: float = Field(..., alias='Idle Min')

    def to_array(self):
        """Converts model to a list of values in the correct order for the model."""
        return [
            self.Protocol, self.Flow_Duration, self.Tot_Fwd_Pkts, self.Tot_Bwd_Pkts,
            self.TotLen_Fwd_Pkts, self.TotLen_Bwd_Pkts, self.Fwd_Pkt_Len_Max, self.Fwd_Pkt_Len_Min,
            self.Fwd_Pkt_Len_Mean, self.Fwd_Pkt_Len_Std, self.Bwd_Pkt_Len_Max, self.Bwd_Pkt_Len_Min,
            self.Bwd_Pkt_Len_Mean, self.Bwd_Pkt_Len_Std, self.Flow_Byts_s, self.Flow_Pkts_s,
            self.Flow_IAT_Mean, self.Flow_IAT_Std, self.Flow_IAT_Max, self.Flow_IAT_Min,
            self.Fwd_IAT_Tot, self.Fwd_IAT_Mean, self.Fwd_IAT_Std, self.Fwd_IAT_Max, self.Fwd_IAT_Min,
            self.Bwd_IAT_Tot, self.Bwd_IAT_Mean, self.Bwd_IAT_Std, self.Bwd_IAT_Max, self.Bwd_IAT_Min,
            self.Fwd_PSH_Flags, self.Fwd_URG_Flags, self.Fwd_Header_Len, self.Bwd_Header_Len,
            self.Fwd_Pkts_s, self.Bwd_Pkts_s, self.Pkt_Len_Min, self.Pkt_Len_Max,
            self.Pkt_Len_Mean, self.Pkt_Len_Std, self.Pkt_Len_Var, self.FIN_Flag_Cnt,
            self.SYN_Flag_Cnt, self.RST_Flag_Cnt, self.PSH_Flag_Cnt, self.ACK_Flag_Cnt,
            self.URG_Flag_Cnt, self.CWE_Flag_Count, self.ECE_Flag_Cnt, self.Down_Up_Ratio,
            self.Pkt_Size_Avg, self.Fwd_Seg_Size_Avg, self.Bwd_Seg_Size_Avg, self.Subflow_Fwd_Pkts,
            self.Subflow_Fwd_Byts, self.Subflow_Bwd_Pkts, self.Subflow_Bwd_Byts,
            self.Init_Fwd_Win_Byts, self.Init_Bwd_Win_Byts, self.Fwd_Act_Data_Pkts,
            self.Fwd_Seg_Size_Min, self.Active_Mean, self.Active_Std, self.Active_Max,
            self.Active_Min, self.Idle_Mean, self.Idle_Std, self.Idle_Max, self.Idle_Min
        ]
