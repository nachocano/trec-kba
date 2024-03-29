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

/**
 * Offset specifies a range within a field of data in this ContentItem
 */
public class Offset implements org.apache.thrift.TBase<Offset, Offset._Fields>, java.io.Serializable, Cloneable, Comparable<Offset> {
  private static final org.apache.thrift.protocol.TStruct STRUCT_DESC = new org.apache.thrift.protocol.TStruct("Offset");

  private static final org.apache.thrift.protocol.TField TYPE_FIELD_DESC = new org.apache.thrift.protocol.TField("type", org.apache.thrift.protocol.TType.I32, (short)1);
  private static final org.apache.thrift.protocol.TField FIRST_FIELD_DESC = new org.apache.thrift.protocol.TField("first", org.apache.thrift.protocol.TType.I64, (short)2);
  private static final org.apache.thrift.protocol.TField LENGTH_FIELD_DESC = new org.apache.thrift.protocol.TField("length", org.apache.thrift.protocol.TType.I32, (short)3);
  private static final org.apache.thrift.protocol.TField XPATH_FIELD_DESC = new org.apache.thrift.protocol.TField("xpath", org.apache.thrift.protocol.TType.STRING, (short)4);
  private static final org.apache.thrift.protocol.TField CONTENT_FORM_FIELD_DESC = new org.apache.thrift.protocol.TField("content_form", org.apache.thrift.protocol.TType.STRING, (short)5);
  private static final org.apache.thrift.protocol.TField VALUE_FIELD_DESC = new org.apache.thrift.protocol.TField("value", org.apache.thrift.protocol.TType.STRING, (short)6);

  private static final Map<Class<? extends IScheme>, SchemeFactory> schemes = new HashMap<Class<? extends IScheme>, SchemeFactory>();
  static {
    schemes.put(StandardScheme.class, new OffsetStandardSchemeFactory());
    schemes.put(TupleScheme.class, new OffsetTupleSchemeFactory());
  }

  /**
   * see comments on OffsetType
   * 
   * @see OffsetType
   */
  public OffsetType type; // required
  /**
   * actual offset, which could be measured in bytes, chars, or lines.
   * The data element identified by 'first' is included, and that
   * identified by first+length is also included.
   * 
   * In set notation,
   *     [first:first+length-1]
   * 
   * or equivalently
   *     [first:first+length)
   * 
   * or in list slicing, like python's:
   *     [first:first+length]
   * 
   * While thrift treats these as signed integers, negative values are
   * meaningless in this context, i.e. we do not end wrap.
   */
  public long first; // required
  public int length; // required
  /**
   * if xpath is not empty, then annotation applies to an offset
   * within data that starts with an XPATH query into XHTML or XML
   */
  public String xpath; // optional
  /**
   * name of the data element inside a ContentItem to which this label
   * applies, e.g. 'raw' 'clean_html' or 'clean_visible'.  Defaults to
   * clean_visible, which is the most common case.
   */
  public String content_form; // optional
  /**
   * bytes specified by this offset extracted from the original; just
   * to assist in debugging
   */
  public ByteBuffer value; // optional

  /** The set of fields this struct contains, along with convenience methods for finding and manipulating them. */
  public enum _Fields implements org.apache.thrift.TFieldIdEnum {
    /**
     * see comments on OffsetType
     * 
     * @see OffsetType
     */
    TYPE((short)1, "type"),
    /**
     * actual offset, which could be measured in bytes, chars, or lines.
     * The data element identified by 'first' is included, and that
     * identified by first+length is also included.
     * 
     * In set notation,
     *     [first:first+length-1]
     * 
     * or equivalently
     *     [first:first+length)
     * 
     * or in list slicing, like python's:
     *     [first:first+length]
     * 
     * While thrift treats these as signed integers, negative values are
     * meaningless in this context, i.e. we do not end wrap.
     */
    FIRST((short)2, "first"),
    LENGTH((short)3, "length"),
    /**
     * if xpath is not empty, then annotation applies to an offset
     * within data that starts with an XPATH query into XHTML or XML
     */
    XPATH((short)4, "xpath"),
    /**
     * name of the data element inside a ContentItem to which this label
     * applies, e.g. 'raw' 'clean_html' or 'clean_visible'.  Defaults to
     * clean_visible, which is the most common case.
     */
    CONTENT_FORM((short)5, "content_form"),
    /**
     * bytes specified by this offset extracted from the original; just
     * to assist in debugging
     */
    VALUE((short)6, "value");

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
        case 1: // TYPE
          return TYPE;
        case 2: // FIRST
          return FIRST;
        case 3: // LENGTH
          return LENGTH;
        case 4: // XPATH
          return XPATH;
        case 5: // CONTENT_FORM
          return CONTENT_FORM;
        case 6: // VALUE
          return VALUE;
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
  private static final int __FIRST_ISSET_ID = 0;
  private static final int __LENGTH_ISSET_ID = 1;
  private byte __isset_bitfield = 0;
  private _Fields optionals[] = {_Fields.XPATH,_Fields.CONTENT_FORM,_Fields.VALUE};
  public static final Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> metaDataMap;
  static {
    Map<_Fields, org.apache.thrift.meta_data.FieldMetaData> tmpMap = new EnumMap<_Fields, org.apache.thrift.meta_data.FieldMetaData>(_Fields.class);
    tmpMap.put(_Fields.TYPE, new org.apache.thrift.meta_data.FieldMetaData("type", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.EnumMetaData(org.apache.thrift.protocol.TType.ENUM, OffsetType.class)));
    tmpMap.put(_Fields.FIRST, new org.apache.thrift.meta_data.FieldMetaData("first", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.I64)));
    tmpMap.put(_Fields.LENGTH, new org.apache.thrift.meta_data.FieldMetaData("length", org.apache.thrift.TFieldRequirementType.DEFAULT, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.I32)));
    tmpMap.put(_Fields.XPATH, new org.apache.thrift.meta_data.FieldMetaData("xpath", org.apache.thrift.TFieldRequirementType.OPTIONAL, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.CONTENT_FORM, new org.apache.thrift.meta_data.FieldMetaData("content_form", org.apache.thrift.TFieldRequirementType.OPTIONAL, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING)));
    tmpMap.put(_Fields.VALUE, new org.apache.thrift.meta_data.FieldMetaData("value", org.apache.thrift.TFieldRequirementType.OPTIONAL, 
        new org.apache.thrift.meta_data.FieldValueMetaData(org.apache.thrift.protocol.TType.STRING        , true)));
    metaDataMap = Collections.unmodifiableMap(tmpMap);
    org.apache.thrift.meta_data.FieldMetaData.addStructMetaDataMap(Offset.class, metaDataMap);
  }

  public Offset() {
    this.content_form = "clean_visible";

  }

  public Offset(
    OffsetType type,
    long first,
    int length)
  {
    this();
    this.type = type;
    this.first = first;
    setFirstIsSet(true);
    this.length = length;
    setLengthIsSet(true);
  }

  /**
   * Performs a deep copy on <i>other</i>.
   */
  public Offset(Offset other) {
    __isset_bitfield = other.__isset_bitfield;
    if (other.isSetType()) {
      this.type = other.type;
    }
    this.first = other.first;
    this.length = other.length;
    if (other.isSetXpath()) {
      this.xpath = other.xpath;
    }
    if (other.isSetContent_form()) {
      this.content_form = other.content_form;
    }
    if (other.isSetValue()) {
      this.value = org.apache.thrift.TBaseHelper.copyBinary(other.value);
;
    }
  }

  public Offset deepCopy() {
    return new Offset(this);
  }

  @Override
  public void clear() {
    this.type = null;
    setFirstIsSet(false);
    this.first = 0;
    setLengthIsSet(false);
    this.length = 0;
    this.xpath = null;
    this.content_form = "clean_visible";

    this.value = null;
  }

  /**
   * see comments on OffsetType
   * 
   * @see OffsetType
   */
  public OffsetType getType() {
    return this.type;
  }

  /**
   * see comments on OffsetType
   * 
   * @see OffsetType
   */
  public Offset setType(OffsetType type) {
    this.type = type;
    return this;
  }

  public void unsetType() {
    this.type = null;
  }

  /** Returns true if field type is set (has been assigned a value) and false otherwise */
  public boolean isSetType() {
    return this.type != null;
  }

  public void setTypeIsSet(boolean value) {
    if (!value) {
      this.type = null;
    }
  }

  /**
   * actual offset, which could be measured in bytes, chars, or lines.
   * The data element identified by 'first' is included, and that
   * identified by first+length is also included.
   * 
   * In set notation,
   *     [first:first+length-1]
   * 
   * or equivalently
   *     [first:first+length)
   * 
   * or in list slicing, like python's:
   *     [first:first+length]
   * 
   * While thrift treats these as signed integers, negative values are
   * meaningless in this context, i.e. we do not end wrap.
   */
  public long getFirst() {
    return this.first;
  }

  /**
   * actual offset, which could be measured in bytes, chars, or lines.
   * The data element identified by 'first' is included, and that
   * identified by first+length is also included.
   * 
   * In set notation,
   *     [first:first+length-1]
   * 
   * or equivalently
   *     [first:first+length)
   * 
   * or in list slicing, like python's:
   *     [first:first+length]
   * 
   * While thrift treats these as signed integers, negative values are
   * meaningless in this context, i.e. we do not end wrap.
   */
  public Offset setFirst(long first) {
    this.first = first;
    setFirstIsSet(true);
    return this;
  }

  public void unsetFirst() {
    __isset_bitfield = EncodingUtils.clearBit(__isset_bitfield, __FIRST_ISSET_ID);
  }

  /** Returns true if field first is set (has been assigned a value) and false otherwise */
  public boolean isSetFirst() {
    return EncodingUtils.testBit(__isset_bitfield, __FIRST_ISSET_ID);
  }

  public void setFirstIsSet(boolean value) {
    __isset_bitfield = EncodingUtils.setBit(__isset_bitfield, __FIRST_ISSET_ID, value);
  }

  public int getLength() {
    return this.length;
  }

  public Offset setLength(int length) {
    this.length = length;
    setLengthIsSet(true);
    return this;
  }

  public void unsetLength() {
    __isset_bitfield = EncodingUtils.clearBit(__isset_bitfield, __LENGTH_ISSET_ID);
  }

  /** Returns true if field length is set (has been assigned a value) and false otherwise */
  public boolean isSetLength() {
    return EncodingUtils.testBit(__isset_bitfield, __LENGTH_ISSET_ID);
  }

  public void setLengthIsSet(boolean value) {
    __isset_bitfield = EncodingUtils.setBit(__isset_bitfield, __LENGTH_ISSET_ID, value);
  }

  /**
   * if xpath is not empty, then annotation applies to an offset
   * within data that starts with an XPATH query into XHTML or XML
   */
  public String getXpath() {
    return this.xpath;
  }

  /**
   * if xpath is not empty, then annotation applies to an offset
   * within data that starts with an XPATH query into XHTML or XML
   */
  public Offset setXpath(String xpath) {
    this.xpath = xpath;
    return this;
  }

  public void unsetXpath() {
    this.xpath = null;
  }

  /** Returns true if field xpath is set (has been assigned a value) and false otherwise */
  public boolean isSetXpath() {
    return this.xpath != null;
  }

  public void setXpathIsSet(boolean value) {
    if (!value) {
      this.xpath = null;
    }
  }

  /**
   * name of the data element inside a ContentItem to which this label
   * applies, e.g. 'raw' 'clean_html' or 'clean_visible'.  Defaults to
   * clean_visible, which is the most common case.
   */
  public String getContent_form() {
    return this.content_form;
  }

  /**
   * name of the data element inside a ContentItem to which this label
   * applies, e.g. 'raw' 'clean_html' or 'clean_visible'.  Defaults to
   * clean_visible, which is the most common case.
   */
  public Offset setContent_form(String content_form) {
    this.content_form = content_form;
    return this;
  }

  public void unsetContent_form() {
    this.content_form = null;
  }

  /** Returns true if field content_form is set (has been assigned a value) and false otherwise */
  public boolean isSetContent_form() {
    return this.content_form != null;
  }

  public void setContent_formIsSet(boolean value) {
    if (!value) {
      this.content_form = null;
    }
  }

  /**
   * bytes specified by this offset extracted from the original; just
   * to assist in debugging
   */
  public byte[] getValue() {
    setValue(org.apache.thrift.TBaseHelper.rightSize(value));
    return value == null ? null : value.array();
  }

  public ByteBuffer bufferForValue() {
    return value;
  }

  /**
   * bytes specified by this offset extracted from the original; just
   * to assist in debugging
   */
  public Offset setValue(byte[] value) {
    setValue(value == null ? (ByteBuffer)null : ByteBuffer.wrap(value));
    return this;
  }

  public Offset setValue(ByteBuffer value) {
    this.value = value;
    return this;
  }

  public void unsetValue() {
    this.value = null;
  }

  /** Returns true if field value is set (has been assigned a value) and false otherwise */
  public boolean isSetValue() {
    return this.value != null;
  }

  public void setValueIsSet(boolean value) {
    if (!value) {
      this.value = null;
    }
  }

  public void setFieldValue(_Fields field, Object value) {
    switch (field) {
    case TYPE:
      if (value == null) {
        unsetType();
      } else {
        setType((OffsetType)value);
      }
      break;

    case FIRST:
      if (value == null) {
        unsetFirst();
      } else {
        setFirst((Long)value);
      }
      break;

    case LENGTH:
      if (value == null) {
        unsetLength();
      } else {
        setLength((Integer)value);
      }
      break;

    case XPATH:
      if (value == null) {
        unsetXpath();
      } else {
        setXpath((String)value);
      }
      break;

    case CONTENT_FORM:
      if (value == null) {
        unsetContent_form();
      } else {
        setContent_form((String)value);
      }
      break;

    case VALUE:
      if (value == null) {
        unsetValue();
      } else {
        setValue((ByteBuffer)value);
      }
      break;

    }
  }

  public Object getFieldValue(_Fields field) {
    switch (field) {
    case TYPE:
      return getType();

    case FIRST:
      return Long.valueOf(getFirst());

    case LENGTH:
      return Integer.valueOf(getLength());

    case XPATH:
      return getXpath();

    case CONTENT_FORM:
      return getContent_form();

    case VALUE:
      return getValue();

    }
    throw new IllegalStateException();
  }

  /** Returns true if field corresponding to fieldID is set (has been assigned a value) and false otherwise */
  public boolean isSet(_Fields field) {
    if (field == null) {
      throw new IllegalArgumentException();
    }

    switch (field) {
    case TYPE:
      return isSetType();
    case FIRST:
      return isSetFirst();
    case LENGTH:
      return isSetLength();
    case XPATH:
      return isSetXpath();
    case CONTENT_FORM:
      return isSetContent_form();
    case VALUE:
      return isSetValue();
    }
    throw new IllegalStateException();
  }

  @Override
  public boolean equals(Object that) {
    if (that == null)
      return false;
    if (that instanceof Offset)
      return this.equals((Offset)that);
    return false;
  }

  public boolean equals(Offset that) {
    if (that == null)
      return false;

    boolean this_present_type = true && this.isSetType();
    boolean that_present_type = true && that.isSetType();
    if (this_present_type || that_present_type) {
      if (!(this_present_type && that_present_type))
        return false;
      if (!this.type.equals(that.type))
        return false;
    }

    boolean this_present_first = true;
    boolean that_present_first = true;
    if (this_present_first || that_present_first) {
      if (!(this_present_first && that_present_first))
        return false;
      if (this.first != that.first)
        return false;
    }

    boolean this_present_length = true;
    boolean that_present_length = true;
    if (this_present_length || that_present_length) {
      if (!(this_present_length && that_present_length))
        return false;
      if (this.length != that.length)
        return false;
    }

    boolean this_present_xpath = true && this.isSetXpath();
    boolean that_present_xpath = true && that.isSetXpath();
    if (this_present_xpath || that_present_xpath) {
      if (!(this_present_xpath && that_present_xpath))
        return false;
      if (!this.xpath.equals(that.xpath))
        return false;
    }

    boolean this_present_content_form = true && this.isSetContent_form();
    boolean that_present_content_form = true && that.isSetContent_form();
    if (this_present_content_form || that_present_content_form) {
      if (!(this_present_content_form && that_present_content_form))
        return false;
      if (!this.content_form.equals(that.content_form))
        return false;
    }

    boolean this_present_value = true && this.isSetValue();
    boolean that_present_value = true && that.isSetValue();
    if (this_present_value || that_present_value) {
      if (!(this_present_value && that_present_value))
        return false;
      if (!this.value.equals(that.value))
        return false;
    }

    return true;
  }

  @Override
  public int hashCode() {
    return 0;
  }

  @Override
  public int compareTo(Offset other) {
    if (!getClass().equals(other.getClass())) {
      return getClass().getName().compareTo(other.getClass().getName());
    }

    int lastComparison = 0;

    lastComparison = Boolean.valueOf(isSetType()).compareTo(other.isSetType());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetType()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.type, other.type);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetFirst()).compareTo(other.isSetFirst());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetFirst()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.first, other.first);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetLength()).compareTo(other.isSetLength());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetLength()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.length, other.length);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetXpath()).compareTo(other.isSetXpath());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetXpath()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.xpath, other.xpath);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetContent_form()).compareTo(other.isSetContent_form());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetContent_form()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.content_form, other.content_form);
      if (lastComparison != 0) {
        return lastComparison;
      }
    }
    lastComparison = Boolean.valueOf(isSetValue()).compareTo(other.isSetValue());
    if (lastComparison != 0) {
      return lastComparison;
    }
    if (isSetValue()) {
      lastComparison = org.apache.thrift.TBaseHelper.compareTo(this.value, other.value);
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
    StringBuilder sb = new StringBuilder("Offset(");
    boolean first = true;

    sb.append("type:");
    if (this.type == null) {
      sb.append("null");
    } else {
      sb.append(this.type);
    }
    first = false;
    if (!first) sb.append(", ");
    sb.append("first:");
    sb.append(this.first);
    first = false;
    if (!first) sb.append(", ");
    sb.append("length:");
    sb.append(this.length);
    first = false;
    if (isSetXpath()) {
      if (!first) sb.append(", ");
      sb.append("xpath:");
      if (this.xpath == null) {
        sb.append("null");
      } else {
        sb.append(this.xpath);
      }
      first = false;
    }
    if (isSetContent_form()) {
      if (!first) sb.append(", ");
      sb.append("content_form:");
      if (this.content_form == null) {
        sb.append("null");
      } else {
        sb.append(this.content_form);
      }
      first = false;
    }
    if (isSetValue()) {
      if (!first) sb.append(", ");
      sb.append("value:");
      if (this.value == null) {
        sb.append("null");
      } else {
        org.apache.thrift.TBaseHelper.toString(this.value, sb);
      }
      first = false;
    }
    sb.append(")");
    return sb.toString();
  }

  public void validate() throws org.apache.thrift.TException {
    // check for required fields
    // check for sub-struct validity
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
      // it doesn't seem like you should have to do this, but java serialization is wacky, and doesn't call the default constructor.
      __isset_bitfield = 0;
      read(new org.apache.thrift.protocol.TCompactProtocol(new org.apache.thrift.transport.TIOStreamTransport(in)));
    } catch (org.apache.thrift.TException te) {
      throw new java.io.IOException(te);
    }
  }

  private static class OffsetStandardSchemeFactory implements SchemeFactory {
    public OffsetStandardScheme getScheme() {
      return new OffsetStandardScheme();
    }
  }

  private static class OffsetStandardScheme extends StandardScheme<Offset> {

    public void read(org.apache.thrift.protocol.TProtocol iprot, Offset struct) throws org.apache.thrift.TException {
      org.apache.thrift.protocol.TField schemeField;
      iprot.readStructBegin();
      while (true)
      {
        schemeField = iprot.readFieldBegin();
        if (schemeField.type == org.apache.thrift.protocol.TType.STOP) { 
          break;
        }
        switch (schemeField.id) {
          case 1: // TYPE
            if (schemeField.type == org.apache.thrift.protocol.TType.I32) {
              struct.type = OffsetType.findByValue(iprot.readI32());
              struct.setTypeIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 2: // FIRST
            if (schemeField.type == org.apache.thrift.protocol.TType.I64) {
              struct.first = iprot.readI64();
              struct.setFirstIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 3: // LENGTH
            if (schemeField.type == org.apache.thrift.protocol.TType.I32) {
              struct.length = iprot.readI32();
              struct.setLengthIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 4: // XPATH
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.xpath = iprot.readString();
              struct.setXpathIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 5: // CONTENT_FORM
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.content_form = iprot.readString();
              struct.setContent_formIsSet(true);
            } else { 
              org.apache.thrift.protocol.TProtocolUtil.skip(iprot, schemeField.type);
            }
            break;
          case 6: // VALUE
            if (schemeField.type == org.apache.thrift.protocol.TType.STRING) {
              struct.value = iprot.readBinary();
              struct.setValueIsSet(true);
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

    public void write(org.apache.thrift.protocol.TProtocol oprot, Offset struct) throws org.apache.thrift.TException {
      struct.validate();

      oprot.writeStructBegin(STRUCT_DESC);
      if (struct.type != null) {
        oprot.writeFieldBegin(TYPE_FIELD_DESC);
        oprot.writeI32(struct.type.getValue());
        oprot.writeFieldEnd();
      }
      oprot.writeFieldBegin(FIRST_FIELD_DESC);
      oprot.writeI64(struct.first);
      oprot.writeFieldEnd();
      oprot.writeFieldBegin(LENGTH_FIELD_DESC);
      oprot.writeI32(struct.length);
      oprot.writeFieldEnd();
      if (struct.xpath != null) {
        if (struct.isSetXpath()) {
          oprot.writeFieldBegin(XPATH_FIELD_DESC);
          oprot.writeString(struct.xpath);
          oprot.writeFieldEnd();
        }
      }
      if (struct.content_form != null) {
        if (struct.isSetContent_form()) {
          oprot.writeFieldBegin(CONTENT_FORM_FIELD_DESC);
          oprot.writeString(struct.content_form);
          oprot.writeFieldEnd();
        }
      }
      if (struct.value != null) {
        if (struct.isSetValue()) {
          oprot.writeFieldBegin(VALUE_FIELD_DESC);
          oprot.writeBinary(struct.value);
          oprot.writeFieldEnd();
        }
      }
      oprot.writeFieldStop();
      oprot.writeStructEnd();
    }

  }

  private static class OffsetTupleSchemeFactory implements SchemeFactory {
    public OffsetTupleScheme getScheme() {
      return new OffsetTupleScheme();
    }
  }

  private static class OffsetTupleScheme extends TupleScheme<Offset> {

    @Override
    public void write(org.apache.thrift.protocol.TProtocol prot, Offset struct) throws org.apache.thrift.TException {
      TTupleProtocol oprot = (TTupleProtocol) prot;
      BitSet optionals = new BitSet();
      if (struct.isSetType()) {
        optionals.set(0);
      }
      if (struct.isSetFirst()) {
        optionals.set(1);
      }
      if (struct.isSetLength()) {
        optionals.set(2);
      }
      if (struct.isSetXpath()) {
        optionals.set(3);
      }
      if (struct.isSetContent_form()) {
        optionals.set(4);
      }
      if (struct.isSetValue()) {
        optionals.set(5);
      }
      oprot.writeBitSet(optionals, 6);
      if (struct.isSetType()) {
        oprot.writeI32(struct.type.getValue());
      }
      if (struct.isSetFirst()) {
        oprot.writeI64(struct.first);
      }
      if (struct.isSetLength()) {
        oprot.writeI32(struct.length);
      }
      if (struct.isSetXpath()) {
        oprot.writeString(struct.xpath);
      }
      if (struct.isSetContent_form()) {
        oprot.writeString(struct.content_form);
      }
      if (struct.isSetValue()) {
        oprot.writeBinary(struct.value);
      }
    }

    @Override
    public void read(org.apache.thrift.protocol.TProtocol prot, Offset struct) throws org.apache.thrift.TException {
      TTupleProtocol iprot = (TTupleProtocol) prot;
      BitSet incoming = iprot.readBitSet(6);
      if (incoming.get(0)) {
        struct.type = OffsetType.findByValue(iprot.readI32());
        struct.setTypeIsSet(true);
      }
      if (incoming.get(1)) {
        struct.first = iprot.readI64();
        struct.setFirstIsSet(true);
      }
      if (incoming.get(2)) {
        struct.length = iprot.readI32();
        struct.setLengthIsSet(true);
      }
      if (incoming.get(3)) {
        struct.xpath = iprot.readString();
        struct.setXpathIsSet(true);
      }
      if (incoming.get(4)) {
        struct.content_form = iprot.readString();
        struct.setContent_formIsSet(true);
      }
      if (incoming.get(5)) {
        struct.value = iprot.readBinary();
        struct.setValueIsSet(true);
      }
    }
  }

}

