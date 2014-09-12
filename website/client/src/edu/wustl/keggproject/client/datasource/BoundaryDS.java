/* 
 * Copyright (c) 2011, Eric Xu, Xueyang Feng
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without 
 * modification, are permitted provided that the following conditions are met:
 *
 *  Redistributions of source code must retain the above copyright notice, 
 *  this list of conditions and the following disclaimer.
 *  Redistributions in binary form must reproduce the above copyright notice, 
 *  this list of conditions and the following disclaimer in the documentation 
 *  and/or other materials provided with the distribution.
 *  
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
 *  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
 *  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
 *  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
 *  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
 *  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
 *  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
 *  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
 *  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
 *  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
 *  POSSIBILITY OF SUCH DAMAGE.
 */

package edu.wustl.keggproject.client.datasource;

import com.smartgwt.client.data.DataSourceField;
import com.smartgwt.client.data.RestDataSource;
import com.smartgwt.client.data.fields.DataSourceIntegerField;
import com.smartgwt.client.types.DSDataFormat;
import com.smartgwt.client.types.FieldType;
import com.smartgwt.client.types.RPCTransport;
import edu.wustl.keggproject.client.ConfigurationFactory;

public class BoundaryDS extends RestDataSource {
    private static BoundaryDS _instance = null;
    private static String myurl = ConfigurationFactory.getConfiguration()
            .getBaseUrl() + "model/bound/";

    private BoundaryDS(String id) {
        setID(id);
        setDataFormat(DSDataFormat.JSON);
        setDataTransport(RPCTransport.SCRIPTINCLUDE);
        setCallbackParam("callback");

        DataSourceIntegerField pkField = new DataSourceIntegerField("pk");
        pkField.setHidden(true);
        pkField.setPrimaryKey(true);

        DataSourceField reactionid = new DataSourceField("r", FieldType.TEXT,
                "Reaction ID");
        DataSourceField lb = new DataSourceField("l", FieldType.TEXT, "lb");
        DataSourceField ub = new DataSourceField("u", FieldType.TEXT, "ub");
        setFields(pkField, reactionid, lb, ub);

        setFetchDataURL(myurl + "fetch/");
        setUpdateDataURL(myurl + "update/");
    }

    public static BoundaryDS getInstance() {
        if (_instance == null) {
            _instance = new BoundaryDS("boundary");
            return _instance;
        } else {
            return _instance;
        }
    }
}
