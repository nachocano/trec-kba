/**
 * Autogenerated by Thrift Compiler (0.9.1)
 *
 * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
 *  @generated
 */
package edu.uw.nlp.treckba.gen;

import org.apache.thrift.scheme.IScheme;
import org.apache.thrift.scheme.SchemeFactory;
import org.apache.thrift.scheme.StandardScheme;

import org.apache.thrift.scheme.TupleScheme;
import org.apache.thrift.protocol.TTupleProtocol;
import org.apache.thrift.protocol.TProtocolException;
import org.apache.thrift.EncodingUtils;
import org.apache.thrift.TException;
import org.apache.thrift.async.AsyncMethodCallback;
import org.apache.thrift.server.AbstractNonblockingServer.*;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.EnumMap;
import java.util.Set;
import java.util.HashSet;
import java.util.EnumSet;
import java.util.Collections;
import java.util.BitSet;
import java.nio.ByteBuffer;
import java.util.Arrays;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Tagging implements org.apache.thrift.TBase<Tagging, Tagging._Fields>, java.io.Serializable, Cloneable, Comparable<Tagging> {
  private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("Tagging");

  private static final org.apache.thrift.protocol.TField TAGGER_ID_FIELD_DESC = new org.apache.thrift.protocol.TField("tagger_id", org.apache.thrift.protocol.TType.STRING, (short)1);
  private static final org.apache.thrift.protocol.TField RAW_TAGGING_FIELD_DESC = new org.apache.thrift.protocol.TField("raw_tagging", org.apache.thrift.protocol.TType.STRING, (short)2);
  private static final org.apache.thrift.protocol.TField TAGGER_CONFIG_FIELD_DESC = new org.apache.thrift.protocol.TField("tagger_config", org.apache.thrift.protocol.TType.STRING, (short)3);
  private static final org.apache.thrift.protocol.TField TAGGER_VERSION_FIELD_DESC = new org.apache.thrift.protocol.TField("tagger_version", org.apache.thrift.protocol.TType.STRING, (short)4);
  private static final org.apache.thrift.protocol.TField GENERATION_TIME_FIELD_DESC = new org.apache.thrift.protocol.TField("generation_time", org.apache.thrift.protocol.TType.STRUCT, (short)5);

  private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
  static {
    schemes.put(StandardScheme.class, new TaggingStandardSchemeFactory());
    schemes.put(TupleScheme.class, new TaggingTupleSchemeFactory());
  }

  public String tagger_id; // required
  /**
   * raw output of the tagging tool
   */
  public ByteBuffer raw_tagging; // required
  /**
   * short human-readable description of configuration parameters
   */
  public String tagger_config; // optional
  /**
   * short human-readable version string of the tagging tool
   */
  public String tagger_version; // optional
  /**
   * time that tagging was generated
   */
  public StreamTime generation_time; // optional

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements org.apache.thrift.TFieldIdEnum {
    TAGGER_ID((short)1, "tagger_id"),
    /**
     * raw output of the tagging tool
     */
    RAW_TAGGING((short)2, "raw_tagging"),
    /**
     * short human-readable description of configuration parameters
     */
    TAGGER_CONFIG((short)3, "tagger_config"),
    /**
     * short human-readable version string of the tagging tool
     */
    TAGGER_VERSION((short)4, "tagger_version"),
    /**
     * time that tagging was generated
     */
    GENERATION_TIME((short)5, "generation_time");

    private static final Map<String, _Fields> byName = new HashMap<String, _Fields>();

    static {
      for (_Fields field : EnumSet.allOf(_Fields.class)) {
        byName.put(field.getFieldName(), field);
      }
    }

    /**
     * Find the _Fields constant that matches fieldId, or null if its not found.
     */
    public static _Fields findByThriftId(int fieldId) {
      switch(fieldId) {
        case 1: // TAGGER_ID
          return TAGGER_ID;
        case 2: // RAW_TAGGING
          return RAW_TAGGING;
        case 3: // TAGGER_CONFIG
          return TAGGER_CONFIG;
        case 4: // TAGGER_VERSION
          return TAGGER_VERSION;
        case 5: // GENERATION_TIME
          return GENERATION_TIME;
        default:
          return null;
      }
    }

    /**
     * Find the _Fields constant that matches fieldId, throwing an exception
     * if it is not found.
     */
    public static _Fields findByThriftIdOrThrow(int fieldId) {
      _Fields fields = findByThriftId(fieldId);
      if (fields == null) throw new IllegalArgumentException("Field " + fieldId + " doesn't exist!");
      return fields;
    }

    /**
     * Find the _Fields constant that matches name, or null if its not found.
     */
    public static _Fields findByName(String name) {
      return byName.get(name);
    }

    private final short _thriftId;
    private final String _fieldName;

    _Fields(short thriftId, String fieldName) {
      _thriftId = thriftId;
      _fieldName = fieldName;
    }

    public short getThriftFieldId() {
      return _thriftId;
    }

    public String getFieldName() {
      return _fieldName;
    }
  }

  // isset id assignments
  private _Fields optionals[] = {_Fields.TAGGER_CONFIG,_Fields.TAGGER_VERSION,_Fields.GENERATION_TIME};
  public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
  static {
    Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
    tmpMap.put(_Fields.TAGGER_ID, new org.apache.thrift.meta_data.FieldMetaData("tagger_id", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING        , "TaggerID")));
    tmpMap.put(_Fields.RAW_TAGGING, new org.apache.thrift.meta_data.FieldMetaData("raw_tagging", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING        , true)));
    tmpMap.put(_Fields.TAGGER_CONFIG, new org.apache.thrift.meta_data.FieldMetaData("tagger_config", org.apache.thrift.TFieldRequirementType.OPTIONAL, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.TAGGER_VERSION, new org.apache.thrift.meta_data.FieldMetaData("tagger_version", org.apache.thrift.TFieldRequirementType.OPTIONAL, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.GENERATION_TIME, new org.apache.thrift.meta_data.FieldMetaData("generation_time", org.apache.thrift.TFieldRequirementType.OPTIONAL, 
        new org.apache.thrift.meta_data.StructMetaData(org.apache.thrift.protocol.TType.STRUCT, StreamTime.class)));
    metaDataMap = Collections.unmodifiableMap(tmpMap);
    org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(Tagging.class, metaDataMap);
  }

  public Tagging() {
  }

  public Tagging(
    String tagger_id,
    ByteBuffer raw_tagging)
  {
    this();
    this.tagger_id = tagger_id;
    this.raw_tagging = raw_tagging;
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public Tagging(Tagging other) {
    if (other.isSetTagger_id()) {
      this.tagger_id = other.tagger_id;
    }
    if (other.isSetRaw_tagging()) {
      this.raw_tagging = org.apache.thrift.TBaseHelper.copyBinary(other.raw_tagging);
;
    }
    if (other.isSetTagger_config()) {
      this.tagger_config = other.tagger_config;
    }
    if (other.isSetTagger_version()) {
      this.tagger_version = other.tagger_version;
    }
    if (other.isSetGeneration_time()) {
      this.generation_time = new StreamTime(other.generation_time);
    }
  }

  public Tagging deepCopy() {
    return new Tagging(this);
  }

  @Override
  public void clear() {
    this.tagger_id = null;
    this.raw_tagging = null;
    this.tagger_config = null;
    this.tagger_version = null;
    this.generation_time = null;
  }

  public String getTagger_id() {
    return this.tagger_id;
  }

  public Tagging setTagger_id(String tagger_id) {
    this.tagger_id = tagger_id;
    return this;
  }

  public void unsetTagger_id() {
    this.tagger_id = null;
  }

  /** Returns true if field tagger_id is set (has been assigned a value) and false otherwise */
  public boolean isSetTagger_id() {
    return this.tagger_id != null;
  }

  public void setTagger_idIsSet(boolean value) {
    if (!value) {
      this.tagger_id = null;
    }
  }

  /**
   * raw output of the tagging tool
   */
  public byte[] getRaw_tagging() {
    setRaw_tagging(org.apache.thrift.TBaseHelper.rightSize(raw_tagging));
    return raw_tagging == null ? null : raw_tagging.array();
  }

  public ByteBuffer bufferForRaw_tagging() {
    return raw_tagging;
  }

  /**
   * raw output of the tagging tool
   */
  public Tagging setRaw_tagging(byte[] raw_tagging) {
    setRaw_tagging(raw_tagging == null ? (ByteBuffer)null : ByteBuffer.wrap(raw_tagging));
    return this;
  }

  public Tagging setRaw_tagging(ByteBuffer raw_tagging) {
    this.raw_tagging = raw_tagging;
    return this;
  }

  public void unsetRaw_tagging() {
    this.raw_tagging = null;
  }

  /** Returns true if field raw_tagging is set (has been assigned a value) and false otherwise */
  public boolean isSetRaw_tagging() {
    return this.raw_tagging != null;
  }

  public void setRaw_taggingIsSet(boolean value) {
    if (!value) {
      this.raw_tagging = null;
    }
  }

  /**
   * short human-readable description of configuration parameters
   */
  public String getTagger_config() {
    return this.tagger_config;
  }

  /**
   * short human-readable description of configuration parameters
   */
  public Tagging setTagger_config(String tagger_config) {
    this.tagger_config = tagger_config;
    return this;
  }

  public void unsetTagger_config() {
    this.tagger_config = null;
  }

  /** Returns true if field tagger_config is set (has been assigned a value) and false otherwise */
  public boolean isSetTagger_config() {
    return this.tagger_config != null;
  }

  public void setTagger_configIsSet(boolean value) {
    if (!value) {
      this.tagger_config = null;
    }
  }

  /**
   * short human-readable version string of the tagging tool
   */
  public String getTagger_version() {
    return this.tagger_version;
  }

  /**
   * short human-readable version string of the tagging tool
   */
  public Tagging setTagger_version(String tagger_version) {
    this.tagger_version = tagger_version;
    return this;
  }

  public void unsetTagger_version() {
    this.tagger_version = null;
  }

  /** Returns true if field tagger_version is set (has been assigned a value) and false otherwise */
  public boolean isSetTagger_version() {
    return this.tagger_version != null;
  }

  public void setTagger_versionIsSet(boolean value) {
    if (!value) {
      this.tagger_version = null;
    }
  }

  /**
   * time that tagging was generated
   */
  public StreamTime getGeneration_time() {
    return this.generation_time;
  }

  /**
   * time that tagging was generated
   */
  public Tagging setGeneration_time(StreamTime generation_time) {
    this.generation_time = generation_time;
    return this;
  }

  public void unsetGeneration_time() {
    this.generation_time = null;
  }

  /** Returns true if field generation_time is set (has been assigned a value) and false otherwise */
  public boolean isSetGeneration_time() {
    return this.generation_time != null;
  }

  public void setGeneration_timeIsSet(boolean value) {
    if (!value) {
      this.generation_time = null;
    }
  }

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case TAGGER_ID:
      if (value == null) {
        unsetTagger_id();
      } else {
        setTagger_id((String)value);
      }
      break;

    case RAW_TAGGING:
      if (value == null) {
        unsetRaw_tagging();
      } else {
        setRaw_tagging((ByteBuffer)value);
      }
      break;

    case TAGGER_CONFIG:
      if (value == null) {
        unsetTagger_config();
      } else {
        setTagger_config((String)value);
      }
      break;

    case TAGGER_VERSION:
      if (value == null) {
        unsetTagger_version();
      } else {
        setTagger_version((String)value);
      }
      break;

    case GENERATION_TIME:
      if (value == null) {
        unsetGeneration_time();
      } else {
        setGeneration_time((StreamTime)value);
      }
      break;

    }
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case TAGGER_ID:
      return getTagger_id();

    case RAW_TAGGING:
      return getRaw_tagging();

    case TAGGER_CONFIG:
      return getTagger_config();

    case TAGGER_VERSION:
      return getTagger_version();

    case GENERATION_TIME:
      return getGeneration_time();

    }
    throw new IllegalStateException();
  }

  /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    if (field == null) {
      throw new IllegalArgumentException();
    }

    switch (field) {
    case TAGGER_ID:
      return isSetTagger_id();
    case RAW_TAGGING:
      return isSetRaw_tagging();
    case TAGGER_CONFIG:
      return isSetTagger_config();
    case TAGGER_VERSION:
      return isSetTagger_version();
    case GENERATION_TIME:
      return isSetGeneration_time();
    }
    throw new IllegalStateException();
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof Tagging)
      return this.equals((Tagging)that);
    return false;
  }

  public boolean equals(Tagging that) {
    if (that == null)
      return false;

    boolean this_present_tagger_id = true && this.isSetTagger_id();
    boolean that_present_tagger_id = true && that.isSetTagger_id();
    if (this_present_tagger_id || that_present_tagger_id) {
      if (!(this_present_tagger_id && that_present_tagger_id))
        return false;
      if (!this.tagger_id.equals(that.tagger_id))
        return false;
    }

    boolean this_present_raw_tagging = true && this.isSetRaw_tagging();
    boolean that_present_raw_tagging = true && that.isSetRaw_tagging();
    if (this_present_raw_tagging || that_present_raw_tagging) {
      if (!(this_present_raw_tagging && that_present_raw_tagging))
        return false;
      if (!this.raw_tagging.equals(that.raw_tagging))
        return false;
    }

    boolean this_present_tagger_config = true && this.isSetTagger_config();
    boolean that_present_tagger_config = true && that.isSetTagger_config();
    if (this_present_tagger_config || that_present_tagger_config) {
      if (!(this_present_tagger_config && that_present_tagger_config))
        return false;
      if (!this.tagger_config.equals(that.tagger_config))
        return false;
    }

    boolean this_present_tagger_version = true && this.isSetTagger_version();
    boolean that_present_tagger_version = true && that.isSetTagger_version();
    if (this_present_tagger_version || that_present_tagger_version) {
      if (!(this_present_tagger_version && that_present_tagger_version))
        return false;
      if (!this.tagger_version.equals(that.tagger_version))
        return false;
    }

    boolean this_present_generation_time = true && this.isSetGeneration_time();
    boolean that_present_generation_time = true && that.isSetGeneration_time();
    if (this_present_generation_time || that_present_generation_time) {
      if (!(this_present_generation_time && that_present_generation_time))
        return false;
      if (!this.generation_time.equals(that.generation_time))
        return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    return 0;
  }

  @Override
  public int compareTo(Tagging other) {
    if (!getClass().equals(other.getClass())) {
      return getClass().getName().compareTo(other.getClass().getName());
    }

    int lastComparison = 0;

    lastComparison = Boolean.valueOf(isSetTagger_id()).compareTo(other.isSetTagger_id());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetTagger_id()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.tagger_id, other.tagger_id);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetRaw_tagging()).compareTo(other.isSetRaw_tagging());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetRaw_tagging()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.raw_tagging, other.raw_tagging);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetTagger_config()).compareTo(other.isSetTagger_config());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetTagger_config()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.tagger_config, other.tagger_config);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetTagger_version()).compareTo(other.isSetTagger_version());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetTagger_version()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.tagger_version, other.tagger_version);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetGeneration_time()).compareTo(other.isSetGeneration_time());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetGeneration_time()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.generation_time, other.generation_time);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    return 0;
  }

  public _Fields fieldForId(int fieldId) {
    return _Fields.findByThriftId(fieldId);
  }

  public void read(org.apache.thrift.protocol.TProtocol iprot) throws org.apache.thrift.TException {
    schemes.get(iprot.getScheme()).getScheme().read(iprot, this);
  }

  public void write(org.apache.thrift.protocol.TProtocol oprot) throws org.apache.thrift.TException {
    schemes.get(oprot.getScheme()).getScheme().write(oprot, this);
  }

  @Override
  public String toString() {
    StringBuilder sb = new StringBuilder("Tagging(");
    boolean first = true;

    sb.append("tagger_id:");
    if (this.tagger_id == null) {
      sb.append("null");
    } else {
      sb.append(this.tagger_id);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("raw_tagging:");
    if (this.raw_tagging == null) {
      sb.append("null");
    } else {
      org.apache.thrift.TBaseHelper.toString(this.raw_tagging, sb);
    }
    first = false;
    if (isSetTagger_config()) {
      if (!first) sb.append(", ");
      sb.append("tagger_config:");
      if (this.tagger_config == null) {
        sb.append("null");
      } else {
        sb.append(this.tagger_config);
      }
      first = false;
    }
    if (isSetTagger_version()) {
      if (!first) sb.append(", ");
      sb.append("tagger_version:");
      if (this.tagger_version == null) {
        sb.append("null");
      } else {
        sb.append(this.tagger_version);
      }
      first = false;
    }
    if (isSetGeneration_time()) {
      if (!first) sb.append(", ");
      sb.append("generation_time:");
      if (this.generation_time == null) {
        sb.append("null");
      } else {
        sb.append(this.generation_time);
      }
      first = false;
    }
    sb.append(")");
    return sb.toString();
  }

  public void validate() throws org.apache.thrift.TException {
    // check for required fields
    // check for sub-struct validity
    if (generation_time != null) {
      generation_time.validate();
    }
  }

  private void writeObject(java.io.ObjectOutputStream out) throws java.io.IOException {
    try {
      write(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(out)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private void readObject(java.io.ObjectInputStream in) throws java.io.IOException, ClassNotFoundException {
    try {
      read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private static class TaggingStandardSchemeFactory implements SchemeFactory {
    public TaggingStandardScheme getScheme() {
      return new TaggingStandardScheme();
    }
  }

  private static class TaggingStandardScheme extends StandardScheme<Tagging> {

    public void read(org.apache.thrift.protocol.TProtocol iprot, Tagging struct) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField schemeField;
      iprot.readStructBegin();
      while (true)
      {
        schemeField = iprot.readFieldBegin();
        if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (schemeField.id) {
          case 1: // TAGGER_ID
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.tagger_id = iprot.readString();
              struct.setTagger_idIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 2: // RAW_TAGGING
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.raw_tagging = iprot.readBinary();
              struct.setRaw_taggingIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 3: // TAGGER_CONFIG
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.tagger_config = iprot.readString();
              struct.setTagger_configIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 4: // TAGGER_VERSION
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.tagger_version = iprot.readString();
              struct.setTagger_versionIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 5: // GENERATION_TIME
            if (schemeField.type == org.apache.thrift.protocol.TType.STRUCT) {
              struct.generation_time = new StreamTime();
              struct.generation_time.read(iprot);
              struct.setGeneration_timeIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          default:
            org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
        }
        iprot.readFieldEnd();
      }
      iprot.readStructEnd();

      // check for required fields of primitive type, which can't be checked in the validate method
      struct.validate();
    }

    public void write(org.apache.thrift.protocol.TProtocol oprot, Tagging struct) throws org.apache.thrift.TException {
      struct.validate();

      oprot.writeStructBegin(STRUCT_DESC);
      if (struct.tagger_id != null) {
        oprot.writeFieldBegin(TAGGER_ID_FIELD_DESC);
        oprot.writeString(struct.tagger_id);
        oprot.writeFieldEnd();
      }
      if (struct.raw_tagging != null) {
        oprot.writeFieldBegin(RAW_TAGGING_FIELD_DESC);
        oprot.writeBinary(struct.raw_tagging);
        oprot.writeFieldEnd();
      }
      if (struct.tagger_config != null) {
        if (struct.isSetTagger_config()) {
          oprot.writeFieldBegin(TAGGER_CONFIG_FIELD_DESC);
          oprot.writeString(struct.tagger_config);
          oprot.writeFieldEnd();
        }
      }
      if (struct.tagger_version != null) {
        if (struct.isSetTagger_version()) {
          oprot.writeFieldBegin(TAGGER_VERSION_FIELD_DESC);
          oprot.writeString(struct.tagger_version);
          oprot.writeFieldEnd();
        }
      }
      if (struct.generation_time != null) {
        if (struct.isSetGeneration_time()) {
          oprot.writeFieldBegin(GENERATION_TIME_FIELD_DESC);
          struct.generation_time.write(oprot);
          oprot.writeFieldEnd();
        }
      }
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

  }

  private static class TaggingTupleSchemeFactory implements SchemeFactory {
    public TaggingTupleScheme getScheme() {
      return new TaggingTupleScheme();
    }
  }

  private static class TaggingTupleScheme extends TupleScheme<Tagging> {

    @Override
    public void write(org.apache.thrift.protocol.TProtocol prot, Tagging struct) throws org.apache.thrift.TException {
      TTupleProtocol oprot = (TTupleProtocol) prot;
      BitSet optionals = new BitSet();
      if (struct.isSetTagger_id()) {
        optionals.set(0);
      }
      if (struct.isSetRaw_tagging()) {
        optionals.set(1);
      }
      if (struct.isSetTagger_config()) {
        optionals.set(2);
      }
      if (struct.isSetTagger_version()) {
        optionals.set(3);
      }
      if (struct.isSetGeneration_time()) {
        optionals.set(4);
      }
      oprot.writeBitSet(optionals, 5);
      if (struct.isSetTagger_id()) {
        oprot.writeString(struct.tagger_id);
      }
      if (struct.isSetRaw_tagging()) {
        oprot.writeBinary(struct.raw_tagging);
      }
      if (struct.isSetTagger_config()) {
        oprot.writeString(struct.tagger_config);
      }
      if (struct.isSetTagger_version()) {
        oprot.writeString(struct.tagger_version);
      }
      if (struct.isSetGeneration_time()) {
        struct.generation_time.write(oprot);
      }
    }

    @Override
    public void read(org.apache.thrift.protocol.TProtocol prot, Tagging struct) throws org.apache.thrift.TException {
      TTupleProtocol iprot = (TTupleProtocol) prot;
      BitSet incoming = iprot.readBitSet(5);
      if (incoming.get(0)) {
        struct.tagger_id = iprot.readString();
        struct.setTagger_idIsSet(true);
      }
      if (incoming.get(1)) {
        struct.raw_tagging = iprot.readBinary();
        struct.setRaw_taggingIsSet(true);
      }
      if (incoming.get(2)) {
        struct.tagger_config = iprot.readString();
        struct.setTagger_configIsSet(true);
      }
      if (incoming.get(3)) {
        struct.tagger_version = iprot.readString();
        struct.setTagger_versionIsSet(true);
      }
      if (incoming.get(4)) {
        struct.generation_time = new StreamTime();
        struct.generation_time.read(iprot);
        struct.setGeneration_timeIsSet(true);
      }
    }
  }

}

