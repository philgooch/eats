//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, vJAXB 2.1.10 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2012.04.06 at 03:37:39 PM NZST 
//


package uk.ac.kcl.cch.eats.eatsml;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlIDREF;
import javax.xml.bind.annotation.XmlRootElement;
import javax.xml.bind.annotation.XmlSchemaType;
import javax.xml.bind.annotation.XmlType;


/**
 * <p>Java class for anonymous complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType>
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;group ref="{http://eats.artefact.org.nz/ns/eatsml/}dates"/>
 *       &lt;attGroup ref="{http://eats.artefact.org.nz/ns/eatsml/}authority_attribute"/>
 *       &lt;attribute name="domain_entity" use="required" type="{http://www.w3.org/2001/XMLSchema}IDREF" />
 *       &lt;attribute name="eats_id" type="{http://www.w3.org/2001/XMLSchema}anySimpleType" />
 *       &lt;attribute name="entity_relationship_type" use="required" type="{http://www.w3.org/2001/XMLSchema}IDREF" />
 *       &lt;attribute name="range_entity" use="required" type="{http://www.w3.org/2001/XMLSchema}IDREF" />
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "", propOrder = {
    "dates"
})
@XmlRootElement(name = "entity_relationship")
public class EntityRelationship {

    protected Dates dates;
    @XmlAttribute(name = "domain_entity", required = true)
    @XmlIDREF
    @XmlSchemaType(name = "IDREF")
    protected Object domainEntity;
    @XmlAttribute(name = "eats_id")
    @XmlSchemaType(name = "anySimpleType")
    protected String eatsId;
    @XmlAttribute(name = "entity_relationship_type", required = true)
    @XmlIDREF
    @XmlSchemaType(name = "IDREF")
    protected Object entityRelationshipType;
    @XmlAttribute(name = "range_entity", required = true)
    @XmlIDREF
    @XmlSchemaType(name = "IDREF")
    protected Object rangeEntity;
    @XmlAttribute(required = true)
    @XmlIDREF
    @XmlSchemaType(name = "IDREF")
    protected Object authority;

    /**
     * Gets the value of the dates property.
     * 
     * @return
     *     possible object is
     *     {@link Dates }
     *     
     */
    public Dates getDates() {
        return dates;
    }

    /**
     * Sets the value of the dates property.
     * 
     * @param value
     *     allowed object is
     *     {@link Dates }
     *     
     */
    public void setDates(Dates value) {
        this.dates = value;
    }

    /**
     * Gets the value of the domainEntity property.
     * 
     * @return
     *     possible object is
     *     {@link Object }
     *     
     */
    public Object getDomainEntity() {
        return domainEntity;
    }

    /**
     * Sets the value of the domainEntity property.
     * 
     * @param value
     *     allowed object is
     *     {@link Object }
     *     
     */
    public void setDomainEntity(Object value) {
        this.domainEntity = value;
    }

    /**
     * Gets the value of the eatsId property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getEatsId() {
        return eatsId;
    }

    /**
     * Sets the value of the eatsId property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setEatsId(String value) {
        this.eatsId = value;
    }

    /**
     * Gets the value of the entityRelationshipType property.
     * 
     * @return
     *     possible object is
     *     {@link Object }
     *     
     */
    public Object getEntityRelationshipType() {
        return entityRelationshipType;
    }

    /**
     * Sets the value of the entityRelationshipType property.
     * 
     * @param value
     *     allowed object is
     *     {@link Object }
     *     
     */
    public void setEntityRelationshipType(Object value) {
        this.entityRelationshipType = value;
    }

    /**
     * Gets the value of the rangeEntity property.
     * 
     * @return
     *     possible object is
     *     {@link Object }
     *     
     */
    public Object getRangeEntity() {
        return rangeEntity;
    }

    /**
     * Sets the value of the rangeEntity property.
     * 
     * @param value
     *     allowed object is
     *     {@link Object }
     *     
     */
    public void setRangeEntity(Object value) {
        this.rangeEntity = value;
    }

    /**
     * Gets the value of the authority property.
     * 
     * @return
     *     possible object is
     *     {@link Object }
     *     
     */
    public Object getAuthority() {
        return authority;
    }

    /**
     * Sets the value of the authority property.
     * 
     * @param value
     *     allowed object is
     *     {@link Object }
     *     
     */
    public void setAuthority(Object value) {
        this.authority = value;
    }

}
