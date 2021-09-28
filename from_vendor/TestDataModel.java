package com.uni_t.multimeter.bean;

import android.util.Log;
import androidx.exifinterface.media.ExifInterface;
import com.uni_t.multimeter.C1757R;
import com.uni_t.multimeter.utils.FileUtils;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class TestDataModel {
    public static final int FUNCTION_ACA = 17;
    public static final int FUNCTION_ACA2 = 22;
    public static final int FUNCTION_ACDC = 25;
    public static final int FUNCTION_ACV = 0;
    public static final int FUNCTION_AC_DC = 28;
    public static final int FUNCTION_AC_DC3 = 30;
    public static final int FUNCTION_ACmA = 15;
    public static final int FUNCTION_ACmV = 1;
    public static final int FUNCTION_ACuA = 13;
    public static final int FUNCTION_CAP = 9;
    public static final int FUNCTION_CONT = 7;
    public static final int FUNCTION_DCA = 16;
    public static final int FUNCTION_DCA2 = 23;
    public static final int FUNCTION_DCV = 2;
    public static final int FUNCTION_DCmA = 14;
    public static final int FUNCTION_DCmV = 3;
    public static final int FUNCTION_DCuA = 12;
    public static final int FUNCTION_DIDOE = 8;
    public static final int FUNCTION_HFE = 18;
    public static final int FUNCTION_Hz = 4;
    public static final int FUNCTION_INRUSH = 31;
    public static final int FUNCTION_LPF = 24;
    public static final int FUNCTION_LPF2 = 27;
    public static final int FUNCTION_LPF3 = 29;
    public static final int FUNCTION_Live = 19;
    public static final int FUNCTION_LozV = 21;
    public static final int FUNCTION_NCV = 20;
    public static final int FUNCTION_OHM = 6;
    public static final int FUNCTION_Per = 5;
    public static final int FUNCTION_TC = 10;
    public static final int FUNCTION_TF = 11;
    private static final String[] functionStrings = {"ACV", "ACmV", "DCV", "DCmV", "Hz", "%", "OHM", "CONT", "DIDOE", "CAP", "°C", "°F", "DCuA", "ACuA", "DCmA", "ACmA", "DCA", "ACA", "HFE", "Live", "NCV", "LozV", "ACA", "DCA", "LPF", "AC/DC", "LPF", "AC+DC", "LPF", "AC+DC2", "INRUSH", ""};
    private static final String maxOLString = ".OL,O.L,OL.,OL";
    private static final String minOLString = "-.OL,-O.L,-OL.,-OL";
    private static JSONObject olJson = null;
    private String devMac;
    private String function;
    private boolean isAuto;
    private boolean isBarPol;
    private boolean isBattery;
    private boolean isDc;
    private boolean isHold;
    private boolean isHvWarning;
    private boolean isMax;
    private boolean isMin;
    private boolean isPeakMax;
    private boolean isPeakMin;
    private boolean isRel;
    private String liangcheng;
    private int loadProgress;
    private int maxShow;
    private float maxValue;
    private float minValue;
    private String pairName;
    private String showID;
    private int status;
    private String typeName;
    private String unitValue;
    private String value;

    public boolean isMaxOlValue() {
        String str = this.value;
        if (str != null) {
            return maxOLString.contains(str);
        }
        return false;
    }

    public boolean isMinOlValue() {
        String str = this.value;
        if (str == null || !str.contains("-") || !minOLString.contains(this.value)) {
            return false;
        }
        return true;
    }

    public String getShowID() {
        String str = this.showID;
        return str == null ? "" : str;
    }

    public void setShowID(String str) {
        this.showID = str;
    }

    public int getmaxShow() {
        if (this.isMax) {
            return C1757R.mipmap.ic_flag_max;
        }
        if (this.isMin) {
            return C1757R.mipmap.ic_flag_min;
        }
        if (this.isPeakMax) {
            return C1757R.mipmap.ic_flag_pmax;
        }
        if (this.isPeakMin) {
            return C1757R.mipmap.ic_flag_pmin;
        }
        return 0;
    }

    public float getMaxValue() {
        return this.maxValue;
    }

    public void setMaxValue(float f) {
        this.maxValue = f;
    }

    public float getMinValue() {
        return this.minValue;
    }

    public void setMinValue(float f) {
        this.minValue = f;
    }

    public void anylseData(byte[] bArr) {
        JSONObject optJSONObject;
        if (bArr != null && bArr.length > 3) {
            boolean z = false;
            if (bArr[0] == -85 && bArr[1] == -51 && bArr[2] == bArr.length - 3) {
                setFunction(getFunctionString(bArr[3]));
                JSONObject jSONObject = olJson;
                if (!(jSONObject == null || (optJSONObject = jSONObject.optJSONObject(getFunction())) == null)) {
                    StringBuilder sb = new StringBuilder();
                    sb.append(bArr[4] - 48);
                    sb.append("");
                    JSONArray optJSONArray = optJSONObject.optJSONArray(sb.toString());
                    if (optJSONArray == null) {
                        optJSONArray = optJSONObject.optJSONArray((optJSONObject.length() - 1) + "");
                    }
                    if (optJSONArray != null && optJSONArray.length() == 4) {
                        setLiangcheng(optJSONArray.optString(0));
                        setUnitValue(optJSONArray.optString(1));
                        this.maxValue = (float) optJSONArray.optDouble(2);
                        this.minValue = (float) optJSONArray.optDouble(3);
                    }
                }
                setValue(new String(new byte[]{bArr[5], bArr[6], bArr[7], bArr[8], bArr[9], bArr[10], bArr[11]}));
                this.loadProgress = (bArr[12] * 10) + bArr[13];
                this.isMax = (bArr[14] & 8) != 0;
                this.isMin = (bArr[14] & 4) != 0;
                this.isHold = (bArr[14] & 2) != 0;
                this.isRel = (bArr[14] & 1) != 0;
                this.isAuto = (bArr[15] & 4) == 0;
                this.isBattery = (bArr[15] & 2) != 0;
                this.isHvWarning = (bArr[15] & 1) != 0;
                this.isDc = (bArr[16] & 8) == 0;
                this.isPeakMax = (bArr[16] & 4) != 0;
                this.isPeakMin = (2 & bArr[16]) != 0;
                if ((bArr[16] & 1) != 0) {
                    z = true;
                }
                this.isBarPol = z;
            }
        }
    }

    public static TestDataModel getInstanceFromBytes(byte[] bArr) {
        TestDataModel testDataModel = new TestDataModel();
        testDataModel.anylseData(bArr);
        return testDataModel;
    }

    private static String getFunctionString(int i) {
        if (i >= 0) {
            String[] strArr = functionStrings;
            if (i < strArr.length) {
                return strArr[i];
            }
        }
        String[] strArr2 = functionStrings;
        return strArr2[strArr2.length - 1];
    }

    public TestDataModel(String str, String str2) {
        this.pairName = str;
        this.devMac = str2;
        try {
            olJson = FileUtils.INSTANCE.readJsonFromAsset("funOl.json").getJSONObject("OL");
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public TestDataModel() {
        try {
            olJson = FileUtils.INSTANCE.readJsonFromAsset("funOl.json").getJSONObject("OL");
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public String getFunction() {
        return this.function;
    }

    public void setFunction(String str) {
        this.function = str;
    }

    public String getLiangcheng() {
        return this.liangcheng;
    }

    public String getOLCheckLianchang() {
        if ((!this.isPeakMin && !this.isPeakMax) || (!"ACmV".equals(this.function) && !"ACV".equals(this.function) && !"ACA".equals(this.function) && !"ACuA".equals(this.function) && !"ACmA".equals(this.function))) {
            return this.liangcheng;
        }
        if (("1000V".equals(this.liangcheng) || "20A".equals(this.liangcheng)) && this.typeName.contains(ExifInterface.LONGITUDE_EAST)) {
            String str = "e_" + this.function.toLowerCase() + "_peak_" + this.liangcheng;
            Log.e("TestDataModel", str);
            return str;
        }
        Log.e("TestDataModel", this.function.toLowerCase() + "_peak_" + this.liangcheng);
        return this.function.toLowerCase() + "_peak_" + this.liangcheng;
    }

    public void setLiangcheng(String str) {
        this.liangcheng = str;
    }

    public String getValue() {
        return this.value;
    }

    public float getValueNumber() {
        try {
            if (this.value != null) {
                return Float.parseFloat(this.value.trim());
            }
            return 0.0f;
        } catch (Exception unused) {
            return 0.0f;
        }
    }

    public void setValue(String str) {
        this.value = str.replaceAll(" ", "");
    }

    public int getLoadProgress() {
        return this.loadProgress;
    }

    public void setLoadProgress(int i) {
        this.loadProgress = i;
    }

    public boolean isMax() {
        return this.isMax;
    }

    public void setMax(boolean z) {
        this.isMax = z;
    }

    public boolean isMin() {
        return this.isMin;
    }

    public void setMin(boolean z) {
        this.isMin = z;
    }

    public boolean isHold() {
        return this.isHold;
    }

    public boolean isPer() {
        return "%".equals(getFunction());
    }

    public void setHold(boolean z) {
        this.isHold = z;
    }

    public boolean isRel() {
        return this.isRel;
    }

    public void setRel(boolean z) {
        this.isRel = z;
    }

    public boolean isAuto() {
        return this.isAuto;
    }

    public void setAuto(boolean z) {
        this.isAuto = z;
    }

    public boolean isBattery() {
        return this.isBattery;
    }

    public void setBattery(boolean z) {
        this.isBattery = z;
    }

    public boolean isHvWarning() {
        return this.isHvWarning;
    }

    public void setHvWarning(boolean z) {
        this.isHvWarning = z;
    }

    public boolean isDc() {
        return this.isDc;
    }

    public void setDc(boolean z) {
        this.isDc = z;
    }

    public boolean isPeakMax() {
        return this.isPeakMax;
    }

    public void setPeakMax(boolean z) {
        this.isPeakMax = z;
    }

    public boolean isPeakMin() {
        return this.isPeakMin;
    }

    public void setPeakMin(boolean z) {
        this.isPeakMin = z;
    }

    public boolean isBarPol() {
        return this.isBarPol;
    }

    public void setBarPol(boolean z) {
        this.isBarPol = z;
    }

    public String getPairName() {
        return this.pairName;
    }

    public void setPairName(String str) {
        this.pairName = str;
    }

    public String getTypeName() {
        String str = this.typeName;
        if (str == null || str.isEmpty()) {
            return this.pairName;
        }
        return this.typeName;
    }

    public void setTypeName(String str) {
        JSONObject optJSONObject;
        this.typeName = str;
        FileUtils fileUtils = FileUtils.INSTANCE;
        JSONObject readJsonFromAsset = fileUtils.readJsonFromAsset("funOl_" + str + ".json");
        if (readJsonFromAsset == null) {
            readJsonFromAsset = FileUtils.INSTANCE.readJsonFromAsset("funOl.json");
        }
        if (readJsonFromAsset != null && (optJSONObject = readJsonFromAsset.optJSONObject("OL")) != null) {
            olJson = optJSONObject;
        }
    }

    public String getDevMac() {
        return this.devMac;
    }

    public void setDevMac(String str) {
        this.devMac = str;
    }

    public int getStatus() {
        return this.status;
    }

    public void setStatus(int i) {
        this.status = i;
    }

    public String getUnitValue() {
        return this.unitValue;
    }

    public void setUnitValue(String str) {
        this.unitValue = str;
    }

    public String toString() {
        return "TestDataModel{function='" + this.function + '\'' + ", liangcheng='" + this.liangcheng + '\'' + ", value='" + this.value + '\'' + ", loadProgress=" + this.loadProgress + ", isMax=" + this.isMax + ", isMin=" + this.isMin + ", isHold=" + this.isHold + ", isRel=" + this.isRel + ", isAuto=" + this.isAuto + ", isBattery=" + this.isBattery + ", isHvWarning=" + this.isHvWarning + ", isDc=" + this.isDc + ", isPeakMax=" + this.isPeakMax + ", isPeakMin=" + this.isPeakMin + ", isBarPol=" + this.isBarPol + ", pairName='" + this.pairName + '\'' + ", typeName='" + this.typeName + '\'' + ", devMac='" + this.devMac + '\'' + ", status=" + this.status + '}';
    }
}
